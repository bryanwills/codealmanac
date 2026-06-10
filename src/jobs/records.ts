import { existsSync } from "node:fs";
import { mkdir, readFile, readdir, rename, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";

import type { OperationSpec } from "../operations/spec.js";
import type { HarnessFailure } from "../harness/events.js";
import { isJsonValue } from "../harness/final-output.js";
import { getRepoAlmanacDir } from "../paths.js";
import type {
  JobOperationOutput,
  JobPageChanges,
  JobRecord,
  JobStatus,
  JobSummary,
  JobView,
} from "./types.js";

export function jobsDir(repoRoot: string): string {
  return join(getRepoAlmanacDir(repoRoot), "jobs");
}

export function legacyRunsDir(repoRoot: string): string {
  return join(getRepoAlmanacDir(repoRoot), "runs");
}

export function jobRecordPath(repoRoot: string, jobId: string): string {
  return join(jobsDir(repoRoot), `${jobId}.json`);
}

export function jobLogPath(repoRoot: string, jobId: string): string {
  return join(jobsDir(repoRoot), `${jobId}.jsonl`);
}

export function jobCancelPath(repoRoot: string, jobId: string): string {
  return join(jobsDir(repoRoot), `${jobId}.cancel`);
}

export async function resolveJobRecordPath(
  repoRoot: string,
  jobId: string,
): Promise<string> {
  const primary = jobRecordPath(repoRoot, jobId);
  if (existsSync(primary)) return primary;
  const legacy = join(legacyRunsDir(repoRoot), `${jobId}.json`);
  if (existsSync(legacy)) return legacy;
  return primary;
}

export async function resolveJobLogPath(
  repoRoot: string,
  jobId: string,
): Promise<string> {
  const primary = jobLogPath(repoRoot, jobId);
  if (existsSync(primary)) return primary;
  const legacy = join(legacyRunsDir(repoRoot), `${jobId}.jsonl`);
  if (existsSync(legacy)) return legacy;
  return primary;
}

export async function resolveJobCancelPath(
  repoRoot: string,
  jobId: string,
): Promise<string> {
  const primary = jobCancelPath(repoRoot, jobId);
  if (existsSync(primary)) return primary;
  const legacy = join(legacyRunsDir(repoRoot), `${jobId}.cancel`);
  if (existsSync(legacy)) return legacy;
  return primary;
}

export async function markJobCancelled(
  repoRoot: string,
  jobId: string,
): Promise<void> {
  const path = await resolveJobCancelPath(repoRoot, jobId);
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, "cancelled\n", "utf8");
}

export function isJobCancellationRequested(
  repoRoot: string,
  jobId: string,
): boolean {
  return existsSync(jobCancelPath(repoRoot, jobId)) ||
    existsSync(join(legacyRunsDir(repoRoot), `${jobId}.cancel`));
}

export async function writeJobRecord(
  path: string,
  record: JobRecord,
): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  const tmp = `${path}.tmp-${process.pid}`;
  await writeFile(tmp, `${JSON.stringify(record, null, 2)}\n`, "utf8");
  await rename(tmp, path);
}

export function buildStartedJobRecord(args: {
  jobId: string;
  repoRoot: string;
  spec: OperationSpec;
  startedAt: Date;
  pid?: number;
}): JobRecord {
  return {
    version: 1,
    id: args.jobId,
    operation: args.spec.metadata?.operation ?? "absorb",
    status: "running",
    repoRoot: args.repoRoot,
    pid: args.pid ?? process.pid,
    provider: args.spec.provider.id,
    model: args.spec.provider.model,
    startedAt: args.startedAt.toISOString(),
    logPath: jobLogPath(args.repoRoot, args.jobId),
    targetKind: args.spec.metadata?.targetKind,
    targetPaths: args.spec.metadata?.targetPaths,
  };
}

export function buildQueuedJobRecord(args: {
  jobId: string;
  repoRoot: string;
  spec: OperationSpec;
  queuedAt: Date;
}): JobRecord {
  return {
    ...buildStartedJobRecord({
      jobId: args.jobId,
      repoRoot: args.repoRoot,
      spec: args.spec,
      startedAt: args.queuedAt,
      pid: 0,
    }),
    status: "queued",
  };
}

export function finishJobRecord(args: {
  record: JobRecord;
  status: Extract<JobStatus, "done" | "failed" | "cancelled">;
  finishedAt: Date;
  providerSessionId?: string;
  summary?: JobSummary;
  pageChanges?: JobPageChanges;
  operationOutput?: JobOperationOutput;
  error?: string;
  failure?: HarnessFailure;
}): JobRecord {
  const started = Date.parse(args.record.startedAt);
  const finished = args.finishedAt.getTime();
  return {
    ...args.record,
    status: args.status,
    providerSessionId: args.providerSessionId ?? args.record.providerSessionId,
    finishedAt: args.finishedAt.toISOString(),
    durationMs: Number.isFinite(started)
      ? Math.max(0, finished - started)
      : undefined,
    summary: args.summary,
    pageChanges: args.pageChanges,
    operationOutput: args.operationOutput,
    error: args.error,
    failure: args.failure,
  };
}

export async function readJobRecord(path: string): Promise<JobRecord | null> {
  try {
    const parsed = JSON.parse(await readFile(path, "utf8")) as unknown;
    return isJobRecord(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

export async function listJobRecords(repoRoot: string): Promise<JobRecord[]> {
  const records: JobRecord[] = [];
  for (const dir of [jobsDir(repoRoot), legacyRunsDir(repoRoot)]) {
    if (!existsSync(dir)) continue;
    let entries: string[];
    try {
      entries = await readdir(dir);
    } catch {
      continue;
    }
    for (const entry of entries) {
      if (!isJobJsonRecordEntry(entry)) continue;
      const record = await readJobRecord(join(dir, entry));
      if (record !== null && !records.some((existing) => existing.id === record.id)) {
        records.push(record);
      }
    }
  }
  return records.sort((a, b) => b.startedAt.localeCompare(a.startedAt));
}

function isJobJsonRecordEntry(entry: string): boolean {
  return (entry.startsWith("job_") || entry.startsWith("run_")) && entry.endsWith(".json");
}

export function toJobView(args: {
  record: JobRecord;
  now: Date;
  isPidAlive: (pid: number) => boolean;
}): JobView {
  const started = Date.parse(args.record.startedAt);
  const finished =
    args.record.finishedAt !== undefined
      ? Date.parse(args.record.finishedAt)
      : undefined;
  const elapsedMs =
    args.record.durationMs ??
    (Number.isFinite(started)
      ? Math.max(0, (finished ?? args.now.getTime()) - started)
      : 0);
  const displayStatus =
    args.record.status === "running" && !args.isPidAlive(args.record.pid)
      ? "stale"
      : args.record.status;
  return {
    ...args.record,
    displayStatus,
    elapsedMs,
    error:
      displayStatus === "stale"
        ? "process ended without a final status"
        : args.record.error,
  };
}

export function isJobRecord(value: unknown): value is JobRecord {
  if (value === null || typeof value !== "object") return false;
  const v = value as Partial<JobRecord>;
  return (
    v.version === 1 &&
    typeof v.id === "string" &&
    isJobId(v.id) &&
    (v.operation === "build" || v.operation === "absorb" || v.operation === "garden") &&
    (v.status === "queued" ||
      v.status === "running" ||
      v.status === "done" ||
      v.status === "failed" ||
      v.status === "cancelled") &&
    typeof v.repoRoot === "string" &&
    typeof v.pid === "number" &&
    (v.provider === "claude" || v.provider === "codex" || v.provider === "cursor") &&
    typeof v.startedAt === "string" &&
    typeof v.logPath === "string" &&
    (v.pageChanges === undefined || isJobPageChanges(v.pageChanges)) &&
    (v.operationOutput === undefined || isJobOperationOutput(v.operationOutput))
  );
}

function isJobOperationOutput(value: unknown): value is JobOperationOutput {
  if (value === null || typeof value !== "object") return false;
  const v = value as Partial<JobOperationOutput>;
  return (
    v.version === 1 &&
    typeof v.contract === "string" &&
    v.contract.length > 0 &&
    isJsonValue(v.value)
  );
}

function isJobPageChanges(value: unknown): value is JobPageChanges {
  if (value === null || typeof value !== "object") return false;
  const v = value as Partial<JobPageChanges>;
  return (
    v.version === 1 &&
    (typeof v.jobId === "string" || typeof (v as { runId?: unknown }).runId === "string") &&
    isStringArray(v.created) &&
    isStringArray(v.updated) &&
    isStringArray(v.archived) &&
    isStringArray(v.deleted) &&
    (v.summary === undefined || typeof v.summary === "string")
  );
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function isJobId(value: string): boolean {
  return value.startsWith("job_") || value.startsWith("run_");
}
