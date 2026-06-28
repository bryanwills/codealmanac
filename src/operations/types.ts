import type { AgentRuntimeProviderId } from "../agent/runtime/types.js";
import type { OperationSpec } from "./spec.js";
import type { AgentRuntimeEvent } from "../agent/runtime/events.js";
import type {
  JobWorkerProgram,
  StartBackgroundJobResult,
  StartJobResult,
} from "../jobs/index.js";

export type { JobWorkerProgram };

export interface OperationProviderSelection {
  id: AgentRuntimeProviderId;
  model?: string;
  effort?: string;
}

export type OperationMode = "foreground" | "background";

export interface OperationRunResult {
  mode: OperationMode;
  jobId: string;
  foreground?: StartJobResult;
  background?: StartBackgroundJobResult;
}

export type StartForegroundJob = (options: {
  repoRoot: string;
  spec: OperationSpec;
  jobId?: string;
  pid: number;
  workerEnvironment: NodeJS.ProcessEnv;
  onEvent?: (event: AgentRuntimeEvent) => void | Promise<void>;
}) => Promise<StartJobResult>;

export type StartBackgroundJob = (options: {
  repoRoot: string;
  spec: OperationSpec;
  jobId?: string;
  workerProgram: JobWorkerProgram;
  workerEnvironment: NodeJS.ProcessEnv;
}) => Promise<StartBackgroundJobResult>;
