import { readFile } from "node:fs/promises";

import type { CommandResult } from "../helpers.js";
import { renderError, renderOutcome } from "../outcome.js";
import { UserFacingError } from "../../errors.js";
import { findNearestAlmanacDir } from "../../paths.js";
import { formatTextTable } from "./table.js";
import {
  finishJobRecord,
  markJobCancelled,
  listJobRecords,
  readJobRecord,
  resolveJobLogPath,
  resolveJobRecordPath,
  toJobView,
  writeJobRecord,
} from "../../jobs/index.js";
import type { JobView } from "../../jobs/index.js";

export interface JobsOptions {
  cwd: string;
  json?: boolean;
  now?: () => Date;
  isPidAlive?: (pid: number) => boolean;
}

export interface JobByIdOptions extends JobsOptions {
  jobId: string;
}

export interface JobAttachStreamOptions extends JobByIdOptions {
  write?: (chunk: string) => void;
  pollMs?: number;
}

export async function runJobsList(
  options: JobsOptions,
): Promise<CommandResult> {
  const repoRoot = resolveWikiOrResult(options.cwd, options.json);
  if (typeof repoRoot !== "string") return repoRoot;

  const views = await listJobViews(repoRoot, options);
  if (options.json === true) {
    return {
      stdout: `${JSON.stringify({ jobs: views }, null, 2)}\n`,
      stderr: "",
      exitCode: 0,
    };
  }

  if (views.length === 0) {
    return { stdout: "Jobs\n\nNo jobs found.\n", stderr: "", exitCode: 0 };
  }
  const lines = ["Jobs", "", ...formatJobRows(views)];
  return { stdout: `${lines.join("\n")}\n`, stderr: "", exitCode: 0 };
}

export async function runJobsShow(
  options: JobByIdOptions,
): Promise<CommandResult> {
  const repoRoot = resolveWikiOrResult(options.cwd, options.json);
  if (typeof repoRoot !== "string") return repoRoot;
  const view = await readJobView(repoRoot, options);
  if (view === null) return missingJob(options.jobId, options.json);

  if (options.json === true) {
    return {
      stdout: `${JSON.stringify(view, null, 2)}\n`,
      stderr: "",
      exitCode: 0,
    };
  }

  return {
    stdout:
      [
        `Job: ${view.id}`,
        `Operation: ${view.operation}`,
        `Status: ${view.displayStatus}`,
        `Provider: ${view.provider}${view.model !== undefined ? `/${view.model}` : ""}`,
        `Elapsed: ${formatMs(view.elapsedMs)}`,
        `Log: ${view.logPath}`,
        view.pageChanges?.description !== undefined
          ? `Description: ${view.pageChanges.description}`
          : undefined,
        ...formatPageChanges(view),
        view.failure !== undefined
          ? `Reason: ${view.failure.message}`
          : view.error !== undefined
            ? `Error: ${view.error}`
            : undefined,
        view.failure?.fix !== undefined ? `Fix: ${view.failure.fix}` : undefined,
      ].filter((line): line is string => line !== undefined).join("\n") + "\n",
    stderr: "",
    exitCode: 0,
  };
}

function formatPageChanges(view: JobView): string[] {
  const changes = view.pageChanges;
  if (changes === undefined) return [];
  const total =
    changes.created.length +
    changes.updated.length +
    changes.deleted.length;
  if (total === 0) return ["Changes: none"];
  const lines = [
    `Changes: ${changes.created.length} created, ${changes.updated.length} updated, ${changes.deleted.length} deleted`,
  ];
  for (const [label, slugs] of [
    ["Created", changes.created],
    ["Updated", changes.updated],
    ["Deleted", changes.deleted],
  ] as const) {
    if (slugs.length > 0) lines.push(`${label}: ${slugs.join(", ")}`);
  }
  return lines;
}

export async function runJobsLogs(
  options: JobByIdOptions,
): Promise<CommandResult> {
  const repoRoot = resolveWikiOrResult(options.cwd, options.json);
  if (typeof repoRoot !== "string") return repoRoot;
  const record = await readJobRecord(await resolveJobRecordPath(repoRoot, options.jobId));
  if (record === null) return missingJob(options.jobId, options.json);
  try {
    const logPath = await resolveJobLogPath(repoRoot, record.id);
    return {
      stdout: await readFile(logPath, "utf8"),
      stderr: "",
      exitCode: 0,
    };
  } catch (err: unknown) {
    return renderOutcome(
      {
        type: "error",
        message: err instanceof Error ? err.message : String(err),
      },
      { json: options.json },
    );
  }
}

export async function runJobsAttach(
  options: JobByIdOptions,
): Promise<CommandResult> {
  const logs = await runJobsLogs(options);
  if (logs.exitCode !== 0 || options.json === true) return logs;
  return {
    ...logs,
    stdout:
      logs.stdout.length > 0
        ? logs.stdout
        : "No log events have been written yet.\n",
  };
}

export async function streamJobsAttach(
  options: JobAttachStreamOptions,
): Promise<CommandResult> {
  const repoRoot = resolveWikiOrResult(options.cwd, options.json);
  if (typeof repoRoot !== "string") return repoRoot;
  const initial = await readJobRecord(await resolveJobRecordPath(repoRoot, options.jobId));
  if (initial === null) return missingJob(options.jobId, options.json);

  const write = options.write ?? ((chunk: string) => process.stdout.write(chunk));
  let offset = 0;
  while (true) {
    const record = await readJobRecord(await resolveJobRecordPath(repoRoot, options.jobId));
    if (record === null) return missingJob(options.jobId, options.json);
    offset = await writeLogChunk(
      await resolveJobLogPath(repoRoot, record.id),
      offset,
      write,
    );
    const view = toJobView({
      record,
      now: options.now?.() ?? new Date(),
      isPidAlive: options.isPidAlive ?? isPidAlive,
    });
    if (
      view.displayStatus === "done" ||
      view.displayStatus === "failed" ||
      view.displayStatus === "cancelled" ||
      view.displayStatus === "stale"
    ) {
      const message = terminalAttachMessage(view);
      if (message.length > 0) write(message);
      return { stdout: "", stderr: "", exitCode: 0 };
    }
    await sleep(options.pollMs ?? 500);
  }
}

export async function runJobsCancel(
  options: JobByIdOptions,
): Promise<CommandResult> {
  const repoRoot = resolveWikiOrResult(options.cwd, options.json);
  if (typeof repoRoot !== "string") return repoRoot;
  const path = await resolveJobRecordPath(repoRoot, options.jobId);
  const record = await readJobRecord(path);
  if (record === null) return missingJob(options.jobId, options.json);
  if (record.status === "done" || record.status === "failed" || record.status === "cancelled") {
    return renderOutcome(
      {
        type: "noop",
        message: `job already ${record.status}: ${record.id}`,
        data: { jobId: record.id, status: record.status },
      },
      { json: options.json },
    );
  }

  await markJobCancelled(repoRoot, record.id);

  if (record.pid > 0) {
    try {
      process.kill(record.pid, "SIGTERM");
    } catch {
      // The final record still becomes cancelled; stale detection covers
      // processes that already exited.
    }
  }

  const cancelled = finishJobRecord({
    record,
    status: "cancelled",
    finishedAt: options.now?.() ?? new Date(),
  });
  await writeJobRecord(path, cancelled);
  return renderOutcome(
    {
      type: "success",
      message: `cancelled job: ${record.id}`,
      data: { jobId: record.id, status: "cancelled" },
    },
    { json: options.json },
  );
}

async function listJobViews(
  repoRoot: string,
  options: JobsOptions,
): Promise<JobView[]> {
  const records = await listJobRecords(repoRoot);
  return records.map((record) =>
    toJobView({
      record,
      now: options.now?.() ?? new Date(),
      isPidAlive: options.isPidAlive ?? isPidAlive,
    }),
  );
}

async function readJobView(
  repoRoot: string,
  options: JobByIdOptions,
): Promise<JobView | null> {
  const record = await readJobRecord(await resolveJobRecordPath(repoRoot, options.jobId));
  if (record === null) return null;
  return toJobView({
    record,
    now: options.now?.() ?? new Date(),
    isPidAlive: options.isPidAlive ?? isPidAlive,
  });
}

function resolveWikiOrResult(
  cwd: string,
  json: boolean | undefined,
): string | CommandResult {
  const repoRoot = findNearestAlmanacDir(cwd);
  if (repoRoot !== null) return repoRoot;
  return renderError(
    new UserFacingError(
      "no Almanac wiki found in this directory or any parent",
      {
        outcome: "needs-action",
        fix: "run: almanac init",
      },
    ),
    { json },
  );
}

function missingJob(jobId: string, json: boolean | undefined): CommandResult {
  return renderOutcome(
    { type: "error", message: `job not found: ${jobId}` },
    { json },
  );
}

async function writeLogChunk(
  path: string,
  offset: number,
  write: (chunk: string) => void,
): Promise<number> {
  let text = "";
  try {
    text = await readFile(path, "utf8");
  } catch {
    return offset;
  }
  if (text.length <= offset) return offset;
  const chunk = text.slice(offset);
  write(chunk);
  return text.length;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isPidAlive(pid: number): boolean {
  if (pid <= 0) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function formatMs(ms: number): string {
  if (ms < 1_000) return `${ms}ms`;
  const seconds = Math.round(ms / 1_000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  return `${Math.round(minutes / 60)}h`;
}

function formatJobRows(views: JobView[]): string[] {
  return formatTextTable({
    headers: ["ID", "OPERATION", "STATUS", "ELAPSED"],
    rows: views.map((view) => [
      view.id,
      view.operation,
      view.displayStatus,
      formatMs(view.elapsedMs),
    ]),
  });
}

function terminalAttachMessage(view: JobView): string {
  if (view.displayStatus !== "failed" && view.displayStatus !== "stale") {
    return "";
  }
  const lines = [`job ${view.displayStatus}: ${view.id}`];
  if (view.failure !== undefined) {
    lines.push(`Reason: ${view.failure.message}`);
    if (view.failure.fix !== undefined) lines.push(`Fix: ${view.failure.fix}`);
  } else if (view.error !== undefined) {
    lines.push(`Error: ${view.error}`);
  }
  return `${lines.join("\n")}\n`;
}
