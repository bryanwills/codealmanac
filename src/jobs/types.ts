import type { AgentUsage, AgentRuntimeFailure } from "../agent/runtime/events.js";
import type { JsonValue } from "../agent/runtime/final-output.js";
import type { AgentRuntimeProviderId } from "../agent/runtime/types.js";
import type { OperationKind } from "../operations/spec.js";

export type JobStatus = "queued" | "running" | "done" | "failed" | "cancelled";
export type DisplayJobStatus = JobStatus | "stale";

export interface JobSummary {
  created: number;
  updated: number;
  archived: number;
  deleted: number;
  costUsd?: number;
  turns?: number;
  usage?: AgentUsage;
}

export interface JobPageChanges {
  version: 1;
  jobId: string;
  created: string[];
  updated: string[];
  archived: string[];
  deleted: string[];
  summary?: string;
}

export interface JobOperationOutput {
  version: 1;
  contract: string;
  value: JsonValue;
}

export interface JobRecord {
  version: 1;
  id: string;
  operation: OperationKind;
  status: JobStatus;
  repoRoot: string;
  pid: number;
  provider: AgentRuntimeProviderId;
  model?: string;
  providerSessionId?: string;
  startedAt: string;
  finishedAt?: string;
  durationMs?: number;
  logPath: string;
  targetKind?: string;
  targetPaths?: string[];
  summary?: JobSummary;
  pageChanges?: JobPageChanges;
  operationOutput?: JobOperationOutput;
  error?: string;
  failure?: AgentRuntimeFailure;
}

export interface JobView extends JobRecord {
  displayStatus: DisplayJobStatus;
  elapsedMs: number;
}
