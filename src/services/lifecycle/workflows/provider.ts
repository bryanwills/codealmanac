import * as operations from "../operations/index.js";

export type LifecycleProviderResolution =
  | { status: "resolved"; value: operations.OperationProviderSelection }
  | { status: "failed"; error: unknown };

export function parseLifecycleProviderSelection(
  value: string | undefined,
): operations.OperationProviderSelection {
  return operations.parseUsing(value);
}

export async function resolveWorkflowProvider(options: {
  cwd: string;
  using?: string;
}): Promise<LifecycleProviderResolution> {
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
