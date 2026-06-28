import * as operations from "../operations/index.js";
import { lifecycleOperationRunResultFromOperation } from "../operation-results.js";
import type {
  InitOperationWorkflowOptions,
  LifecycleOperationWorkflowResult,
} from "../workflow-types.js";
import { resolveWorkflowProvider } from "./provider.js";

export async function runInitOperationWorkflow(
  options: InitOperationWorkflowOptions,
): Promise<LifecycleOperationWorkflowResult> {
  const provider = await resolveWorkflowProvider(options);
  if (provider.status === "failed") return provider;

  const background = options.background === true;
  if (options.json === true && !background) {
    return { status: "json-foreground-unsupported" };
  }

  try {
    return {
      status: "completed",
      operation: "init",
      result: lifecycleOperationRunResultFromOperation(
        await operations.build({
          cwd: options.cwd,
          provider: provider.value,
          background,
          context: initOperationContext(options),
          force: options.force,
          onEvent: options.onEvent,
          startForeground: options.startForeground,
          startBackground: options.startBackground,
          workerProgram: options.workerProgram,
          workerEnvironment: options.workerEnvironment,
          pid: options.pid,
          isPidAlive: options.isPidAlive,
          agentRunner: options.agentRunner,
          loadPrompt: options.loadPrompt,
          registryPathEquals: options.registryPathEquals,
        }),
      ),
    };
  } catch (error: unknown) {
    return { status: "failed", error };
  }
}

function initOperationContext(options: {
  force?: boolean;
  yes?: boolean;
}): string {
  return [
    "Command context:",
    "- Command: init",
    `- Force requested: ${options.force === true ? "yes" : "no"}`,
    `- Non-interactive confirmation: ${options.yes === true ? "yes" : "no"}`,
  ].join("\n");
}
