import type { AgentRuntimeEvent, AgentRuntimeResult } from "../../agent/runtime/events.js";
import type { AgentRuntimeRunHooks } from "../../agent/runtime/types.js";
import { drainQueuedJobs } from "../../services/jobs/runtime/queue-drain.js";
import type { OperationSpec } from "../../services/lifecycle/operations/spec.js";

export interface RunJobWorkerOptions {
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

export async function runJobWorker(
  options: RunJobWorkerOptions,
): Promise<void> {
  await drainQueuedJobs(options);
}
