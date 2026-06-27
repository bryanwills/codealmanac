import type { HarnessEvent } from "../../harness/events.js";
import * as absorb from "../../absorb/index.js";
import * as operations from "../../operations/index.js";

export type LifecycleOperationKind = "init" | "absorb" | "garden";

export interface LifecycleOperationDeps {
  startForeground?: operations.StartForegroundJob;
  startBackground?: operations.StartBackgroundJob;
  onEvent?: (event: HarnessEvent) => void | Promise<void>;
}

export interface InitOperationWorkflowOptions extends LifecycleOperationDeps {
  cwd: string;
  using?: string;
  background?: boolean;
  json?: boolean;
  force?: boolean;
  yes?: boolean;
}

export interface AbsorbOperationWorkflowOptions extends LifecycleOperationDeps {
  cwd: string;
  inputs: string[];
  using?: string;
  foreground?: boolean;
  json?: boolean;
  yes?: boolean;
  resolveSource?: absorb.ResolveSourceFn;
}

export interface GardenOperationWorkflowOptions extends LifecycleOperationDeps {
  cwd: string;
  using?: string;
  foreground?: boolean;
  json?: boolean;
  yes?: boolean;
}

export type LifecycleOperationWorkflowResult =
  | {
      status: "completed";
      operation: LifecycleOperationKind;
      result: operations.OperationRunResult;
    }
  | { status: "json-foreground-unsupported" }
  | { status: "failed"; error: unknown };

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
      result: await operations.build({
        cwd: options.cwd,
        provider: provider.value,
        background,
        context: initContext(options),
        force: options.force,
        onEvent: options.onEvent,
        startForeground: options.startForeground,
        startBackground: options.startBackground,
      }),
    };
  } catch (error: unknown) {
    return { status: "failed", error };
  }
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
      result: started.result,
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
      result: await operations.garden({
        cwd: options.cwd,
        provider: provider.value,
        background: options.foreground !== true,
        onEvent: options.onEvent,
        startForeground: options.startForeground,
        startBackground: options.startBackground,
      }),
    };
  } catch (error: unknown) {
    return { status: "failed", error };
  }
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

function initContext(options: InitOperationWorkflowOptions): string {
  return [
    "Command context:",
    `- Command: init`,
    `- Force requested: ${options.force === true ? "yes" : "no"}`,
    `- Non-interactive confirmation: ${options.yes === true ? "yes" : "no"}`,
  ].join("\n");
}
