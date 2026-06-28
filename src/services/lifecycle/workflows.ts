import * as absorb from "./absorb/index.js";
import * as operations from "./operations/index.js";
import {
  lifecycleOperationRunResultFromOperation,
} from "./operation-results.js";
import type {
  AbsorbOperationWorkflowOptions,
  GardenOperationWorkflowOptions,
  InitOperationWorkflowOptions,
  LifecycleOperationWorkflowResult,
  PreparedAbsorbOperationWorkflowOptions,
} from "./workflow-types.js";

type ProviderResolution =
  | { status: "resolved"; value: operations.OperationProviderSelection }
  | { status: "failed"; error: unknown };

export async function runInitOperationWorkflow(
  options: InitOperationWorkflowOptions,
): Promise<LifecycleOperationWorkflowResult> {
  const provider = await resolveProvider(options);
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

export async function runAbsorbOperationWorkflow(
  options: AbsorbOperationWorkflowOptions,
): Promise<LifecycleOperationWorkflowResult> {
  const provider = await resolveProvider(options);
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
  const provider = await resolveProvider(options);
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
        }),
      ),
    };
  } catch (error: unknown) {
    return { status: "failed", error };
  }
}

export async function runGardenOperationWorkflow(
  options: GardenOperationWorkflowOptions,
): Promise<LifecycleOperationWorkflowResult> {
  const provider = await resolveProvider(options);
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
        }),
      ),
    };
  } catch (error: unknown) {
    return { status: "failed", error };
  }
}

export function parseLifecycleProviderSelection(
  value: string | undefined,
): operations.OperationProviderSelection {
  return operations.parseUsing(value);
}

async function resolveProvider(options: {
  cwd: string;
  using?: string;
}): Promise<ProviderResolution> {
  try {
    return {
      status: "resolved",
      value: await operations.resolveProvider({
        cwd: options.cwd,
        using: options.using,
      }),
    };
  } catch (error: unknown) {
    return { status: "failed", error };
  }
}
