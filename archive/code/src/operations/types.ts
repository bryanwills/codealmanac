import type { HarnessProviderId } from "../harness/types.js";
import type { OperationSpec } from "./spec.js";
import type { HarnessEvent } from "../harness/events.js";
import type {
  StartBackgroundJobResult,
  StartJobResult,
} from "../jobs/index.js";

export interface OperationProviderSelection {
  id: HarnessProviderId;
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
  onEvent?: (event: HarnessEvent) => void | Promise<void>;
}) => Promise<StartJobResult>;

export type StartBackgroundJob = (options: {
  repoRoot: string;
  spec: OperationSpec;
  jobId?: string;
}) => Promise<StartBackgroundJobResult>;
