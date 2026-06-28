import type {
  AgentRuntimeFailure,
  AgentRuntimeProviderId,
  AgentRuntimeResult,
} from "../../../shared/agent-runtime/events.js";
import type { OperationSpec } from "../../../shared/operation-spec.js";
import type { OperationPromptLoader } from "../../../shared/operation-prompts.js";
import type { AgentRuntimeEvent } from "../../../shared/agent-runtime/events.js";
import type { AgentRuntimeRunner } from "../../../shared/agent-runtime/runner.js";
import type { JobWorkerProgram } from "../../../shared/worker-program.js";
import type { IsPidAlive } from "../../../shared/pid-liveness.js";

export type { JobWorkerProgram };

export interface OperationProviderSelection {
  id: AgentRuntimeProviderId;
  model?: string;
  effort?: string;
}

export type { OperationPromptLoader };

export type OperationMode = "foreground" | "background";
export type OperationJobStatus =
  | "queued"
  | "running"
  | "done"
  | "failed"
  | "cancelled";

export interface OperationStartedJobRecord {
  status: OperationJobStatus;
  pid: number;
  logPath: string;
  failure?: AgentRuntimeFailure;
}

export interface OperationForegroundStartResult {
  jobId: string;
  record: OperationStartedJobRecord;
  result: AgentRuntimeResult;
}

export interface OperationBackgroundStartResult {
  jobId: string;
  record: OperationStartedJobRecord;
  childPid: number;
}

export interface OperationRunResult {
  mode: OperationMode;
  jobId: string;
  foreground?: OperationForegroundStartResult;
  background?: OperationBackgroundStartResult;
}

export type StartForegroundJob = (options: {
  repoRoot: string;
  spec: OperationSpec;
  jobId?: string;
  pid: number;
  isPidAlive: IsPidAlive;
  onEvent?: (event: AgentRuntimeEvent) => void | Promise<void>;
  agentRunner: AgentRuntimeRunner;
}) => Promise<OperationForegroundStartResult>;

export type StartBackgroundJob = (options: {
  repoRoot: string;
  spec: OperationSpec;
  jobId?: string;
  workerProgram: JobWorkerProgram;
  workerEnvironment: NodeJS.ProcessEnv;
}) => Promise<OperationBackgroundStartResult>;
