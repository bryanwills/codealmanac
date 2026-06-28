import type { AgentRuntimeEvent, AgentRuntimeResult } from "../../../agent/runtime/events.js";
import type { AgentRuntimeRunHooks } from "../../../agent/runtime/types.js";
import type { OperationSpec } from "../../lifecycle/operations/spec.js";
import {
  finishJobRecord,
} from "./record-factory.js";
import {
  readJobRecord,
  resolveJobRecordPath,
  writeJobRecord,
} from "../../../stores/jobs/records.js";
import { acquireJobWorkerLock } from "../../../stores/jobs/worker-lock.js";
import { oldestQueuedJob } from "./queue.js";
import { readJobSpec } from "../../../stores/jobs/specs.js";
import { startQueuedJob } from "./start.js";
import type { JobRecord } from "../../../stores/jobs/types.js";

export interface DrainQueuedJobsOptions {
  repoRoot: string;
  now?: () => Date;
  pid: number;
  workerEnvironment: NodeJS.ProcessEnv;
  onEvent?: (event: AgentRuntimeEvent) => void | Promise<void>;
  harnessRun?: (
    spec: OperationSpec,
    hooks?: AgentRuntimeRunHooks,
  ) => Promise<AgentRuntimeResult>;
}

export async function drainQueuedJobs(
  options: DrainQueuedJobsOptions,
): Promise<void> {
  const now = options.now ?? (() => new Date());
  while (true) {
    const lock = await acquireJobWorkerLock(options.repoRoot, now());
    if (lock === null) return;
    try {
      while (true) {
        const record = await oldestQueuedJob(options.repoRoot);
        if (record === null) break;
        try {
          const spec = await readJobSpec(options.repoRoot, record.id);
          await startQueuedJob({
            repoRoot: options.repoRoot,
            spec,
            jobId: record.id,
            now,
            pid: options.pid,
            workerEnvironment: options.workerEnvironment,
            onEvent: options.onEvent,
            harnessRun: options.harnessRun,
          });
        } catch (err: unknown) {
          await markQueuedJobFailed({
            repoRoot: options.repoRoot,
            record,
            now: now(),
            error: err instanceof Error ? err.message : String(err),
          });
        }
      }
    } finally {
      await lock.release();
    }
    if (await oldestQueuedJob(options.repoRoot) === null) return;
  }
}

async function markQueuedJobFailed(args: {
  repoRoot: string;
  record: JobRecord;
  now: Date;
  error: string;
}): Promise<void> {
  const recordPath = await resolveJobRecordPath(args.repoRoot, args.record.id);
  const current = await readJobRecord(recordPath);
  if (current === null || current.status !== "queued") return;
  await writeJobRecord(
    recordPath,
    finishJobRecord({
      record: current,
      status: "failed",
      finishedAt: args.now,
      error: args.error,
    }),
  );
}
