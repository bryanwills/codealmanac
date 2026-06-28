import type { AgentUsage, AgentRuntimeFailure } from "../../shared/agent-runtime/events.js";
import type { AgentRuntimeProviderId } from "../../shared/agent-runtime/events.js";
import type { OperationOutput } from "../../shared/operation-output.js";
import type { OperationKind } from "../../shared/operation-spec.js";

export type JobStatus = "queued" | "running" | "done" | "failed" | "cancelled";

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
  operationOutput?: OperationOutput;
  error?: string;
  failure?: AgentRuntimeFailure;
}
