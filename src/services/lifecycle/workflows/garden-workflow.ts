import * as operations from "../operations/index.js";
import { lifecycleOperationRunResultFromOperation } from "../operation-results.js";
import type {
  GardenOperationWorkflowOptions,
  LifecycleOperationWorkflowResult,
} from "../workflow-types.js";
import { resolveWorkflowProvider } from "./provider.js";

export async function runGardenOperationWorkflow(
  options: GardenOperationWorkflowOptions,
): Promise<LifecycleOperationWorkflowResult> {
  const provider = await resolveWorkflowProvider(options);
  if (provider.status === "failed") return provider;
  if (options.json === true && options.foreground === true) {
    return { status: "json-foreground-unsupported" };
  }

  try {
    return {
      status: "completed",
      operation: "garden",
      result: lifecycleOperationRunResultFromOperation(
        await operations.garden({
          cwd: options.cwd,
          provider: provider.value,
          background: options.foreground !== true,
          onEvent: options.onEvent,
          startForeground: options.startForeground,
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
