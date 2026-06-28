import * as absorb from "../absorb/index.js";
import * as operations from "../operations/index.js";
import { lifecycleOperationRunResultFromOperation } from "../operation-results.js";
import type {
  AbsorbOperationWorkflowOptions,
  LifecycleOperationWorkflowResult,
  PreparedAbsorbOperationWorkflowOptions,
} from "../workflow-types.js";
import { resolveWorkflowProvider } from "./provider.js";

export async function runAbsorbOperationWorkflow(
  options: AbsorbOperationWorkflowOptions,
): Promise<LifecycleOperationWorkflowResult> {
  const provider = await resolveWorkflowProvider(options);
  if (provider.status === "failed") return provider;
  if (options.json === true && options.foreground === true) {
    return { status: "json-foreground-unsupported" };
  }

  try {
    const started = await absorb.startRun({
      ...options,
      provider: provider.value,
    });
    return {
      status: "completed",
      operation: "absorb",
      result: lifecycleOperationRunResultFromOperation(started.result),
    };
  } catch (error: unknown) {
    return { status: "failed", error };
  }
}

export async function runPreparedAbsorbOperationWorkflow(
  options: PreparedAbsorbOperationWorkflowOptions,
): Promise<LifecycleOperationWorkflowResult> {
  const provider = await resolveWorkflowProvider(options);
  if (provider.status === "failed") return provider;

  try {
    return {
      status: "completed",
      operation: "absorb",
      result: lifecycleOperationRunResultFromOperation(
        await operations.absorb({
          cwd: options.cwd,
          provider: provider.value,
          background: true,
          context: options.context,
          targetKind: options.targetKind,
          targetPaths: options.targetPaths,
          networkAccess: options.networkAccess,
          startBackground: options.startBackground,
          workerProgram: options.workerProgram,
          workerEnvironment: options.workerEnvironment,
          pid: options.pid,
          isPidAlive: options.isPidAlive,
          agentRunner: options.agentRunner,
          loadPrompt: options.loadPrompt,
        }),
      ),
    };
  } catch (error: unknown) {
    return { status: "failed", error };
  }
}
