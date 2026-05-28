import { join } from "node:path";

import type { HarnessEvent, HarnessResult } from "../harness/events.js";
import type { AgentRunSpec, HarnessRunHooks } from "../harness/types.js";
import { getHarnessProvider } from "../harness/providers/index.js";
import { runIndexer } from "../indexer/index.js";
import { createRunId } from "./ids.js";
import { appendRunEvent, initializeRunLog } from "./logs.js";
import {
  buildStartedRunRecord,
  finishRunRecord,
  isRunCancellationRequested,
  readRunRecord,
  runRecordPath,
  writeRunRecord,
} from "./records.js";
import { diffPageSnapshots, snapshotPages } from "./snapshots.js";
import type { RunRecord, RunSummary } from "./types.js";

export interface StartProcessOptions {
  repoRoot: string;
  spec: AgentRunSpec;
  runId?: string;
  now?: () => Date;
  pid?: number;
  onEvent?: (event: HarnessEvent) => void | Promise<void>;
  harnessRun?: (
    spec: AgentRunSpec,
    hooks?: HarnessRunHooks,
  ) => Promise<HarnessResult>;
}

export interface StartProcessResult {
  runId: string;
  record: RunRecord;
  result: HarnessResult;
}

export async function startForegroundProcess(
  options: StartProcessOptions,
): Promise<StartProcessResult> {
  const now = options.now ?? (() => new Date());
  const runId = options.runId ?? createRunId(now());
  const startedAt = now();
  const recordPath = runRecordPath(options.repoRoot, runId);
  const started = buildStartedRunRecord({
    runId,
    repoRoot: options.repoRoot,
    spec: options.spec,
    startedAt,
    pid: options.pid,
  });

  const preStart = await cancelledRecordIfRequested({
    recordPath,
    repoRoot: options.repoRoot,
    runId,
    fallback: started,
    finishedAt: now(),
  });
  if (preStart !== null) {
    return {
      runId,
      record: preStart,
      result: {
        success: false,
        result: "",
        error: "run cancelled before start",
      },
    };
  }

  await writeRunRecord(recordPath, started);
  await initializeRunLog(started.logPath);
  const afterStart = await cancelledRecordIfRequested({
    recordPath,
    repoRoot: options.repoRoot,
    runId,
    fallback: started,
    finishedAt: now(),
  });
  if (afterStart !== null) {
    return {
      runId,
      record: afterStart,
      result: {
        success: false,
        result: "",
        error: "run cancelled before start",
      },
    };
  }

  const harnessRun =
    options.harnessRun ??
    ((spec, hooks) => getHarnessProvider(spec.provider.id).run(spec, hooks));
  const eventWrites: Promise<void>[] = [];

  let result: HarnessResult;
  let finalRecord: RunRecord;
  try {
    const pagesDir = join(options.repoRoot, ".almanac", "pages");
    const before = await snapshotPages(pagesDir);
    try {
      result = await harnessRun(options.spec, {
        onEvent: eventLogger({
          logPath: started.logPath,
          runId,
          now,
          writes: eventWrites,
          recordPath,
          fallbackRecord: started,
          observer: options.onEvent,
        }),
      });
    } catch (err: unknown) {
      result = {
        success: false,
        result: "",
        error: err instanceof Error ? err.message : String(err),
      };
      await appendRunEvent(started.logPath, {
        type: "error",
        error: result.error ?? "unknown error",
      }, now(), { runId, sequence: eventWrites.length + 1 });
    }
    await Promise.allSettled(eventWrites);

    const after = await snapshotPages(pagesDir);
    const delta = diffPageSnapshots(before, after);
    if (result.success) {
      await runIndexer({ repoRoot: options.repoRoot });
    }

    const summary: RunSummary = {
      created: delta.created,
      updated: delta.updated,
      archived: delta.archived,
      costUsd: result.costUsd,
      turns: result.turns,
      usage: result.usage,
    };
    finalRecord = await finishUnlessCancelled({
      recordPath,
      fallback: started,
      status: result.success ? "done" : "failed",
      finishedAt: now(),
      providerSessionId: result.providerSessionId,
      summary,
      error: result.error,
      failure: result.failure,
    });
  } catch (err: unknown) {
    result = {
      success: false,
      result: "",
      error: err instanceof Error ? err.message : String(err),
    };
    try {
      await appendRunEvent(started.logPath, {
        type: "error",
        error: result.error ?? "unknown error",
      }, now(), { runId, sequence: eventWrites.length + 1 });
    } catch {
      // The run record is the source of truth; do not let a broken log write
      // prevent terminal status recording.
    }
    await Promise.allSettled(eventWrites);
    finalRecord = await finishUnlessCancelled({
      recordPath,
      fallback: started,
      status: "failed",
      finishedAt: now(),
      error: result.error,
      failure: result.failure,
    });
  }

  if (finalRecord.status === "cancelled" && result.success) {
    result = {
      success: false,
      result: "",
      error: "run cancelled before final status",
    };
  }
  return { runId, record: finalRecord, result };
}

async function finishUnlessCancelled(args: {
  recordPath: string;
  fallback: RunRecord;
  status: "done" | "failed";
  finishedAt: Date;
  providerSessionId?: string;
  summary?: RunSummary;
  error?: string;
  failure?: import("../harness/events.js").HarnessFailure;
}): Promise<RunRecord> {
  const current = await readRunRecord(args.recordPath);
  if (
    current?.status === "cancelled" ||
    isRunCancellationRequested(args.fallback.repoRoot, args.fallback.id)
  ) {
    return finishCancelled({
      recordPath: args.recordPath,
      fallback: current ?? args.fallback,
      finishedAt: args.finishedAt,
    });
  }
  const base = current ?? args.fallback;
  const finished = finishRunRecord({
    record: base,
    status: args.status,
    finishedAt: args.finishedAt,
    providerSessionId: args.providerSessionId,
    summary: args.summary,
    error: args.error,
    failure: args.failure,
  });
  await writeRunRecord(args.recordPath, finished);
  return finished;
}

async function cancelledRecordIfRequested(args: {
  recordPath: string;
  repoRoot: string;
  runId: string;
  fallback: RunRecord;
  finishedAt: Date;
}): Promise<RunRecord | null> {
  const current = await readRunRecord(args.recordPath);
  if (
    current?.status !== "cancelled" &&
    !isRunCancellationRequested(args.repoRoot, args.runId)
  ) {
    return null;
  }
  return finishCancelled({
    recordPath: args.recordPath,
    fallback: current ?? args.fallback,
    finishedAt: args.finishedAt,
  });
}

async function finishCancelled(args: {
  recordPath: string;
  fallback: RunRecord;
  finishedAt: Date;
}): Promise<RunRecord> {
  const cancelled =
    args.fallback.status === "cancelled"
      ? args.fallback
      : finishRunRecord({
          record: args.fallback,
          status: "cancelled",
          finishedAt: args.finishedAt,
        });
  await writeRunRecord(args.recordPath, cancelled);
  return cancelled;
}

function eventLogger(args: {
  logPath: string;
  runId: string;
  now: () => Date;
  writes: Promise<void>[];
  recordPath: string;
  fallbackRecord: RunRecord;
  observer?: (event: HarnessEvent) => void | Promise<void>;
}): (event: HarnessEvent) => Promise<void> {
  let sequence = 0;
  return (event) => {
    sequence += 1;
    const writes = [
      appendRunEvent(args.logPath, event, args.now(), { runId: args.runId, sequence }),
      persistProviderSessionId({
        recordPath: args.recordPath,
        fallbackRecord: args.fallbackRecord,
        event,
      }),
    ];
    if (args.observer !== undefined) {
      writes.push(Promise.resolve(args.observer(event)));
    }
    const write = Promise.allSettled(writes).then(() => undefined);
    args.writes.push(write);
    return write;
  };
}

async function persistProviderSessionId(args: {
  recordPath: string;
  fallbackRecord: RunRecord;
  event: HarnessEvent;
}): Promise<void> {
  const providerSessionId = providerSessionIdFromEvent(args.event);
  if (providerSessionId === undefined) return;
  const current = await readRunRecord(args.recordPath);
  const record = current ?? args.fallbackRecord;
  if (record.providerSessionId !== undefined) return;
  await writeRunRecord(args.recordPath, {
    ...record,
    providerSessionId,
  });
}

function providerSessionIdFromEvent(event: HarnessEvent): string | undefined {
  if (event.type === "provider_session") {
    return event.providerSessionId;
  }
  if (event.type === "done" && event.providerSessionId !== undefined) {
    return event.providerSessionId;
  }
  return undefined;
}
