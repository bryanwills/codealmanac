export interface SetupGlobalInstallStateOptions {
  installPath?: string | null;
}

export interface SetupGlobalInstallState {
  ephemeral: boolean;
}

export interface SetupGlobalInstallRuntime {
  readState(options?: SetupGlobalInstallStateOptions): SetupGlobalInstallState;
  install(): Promise<void>;
}

export interface RunSetupGlobalInstallOptions {
  runtime: SetupGlobalInstallRuntime;
}

export type SetupGlobalInstallResult =
  | { ok: true }
  | { ok: false; error: string };

export function readSetupGlobalInstallState(
  options: SetupGlobalInstallStateOptions & {
    runtime: SetupGlobalInstallRuntime;
  },
): SetupGlobalInstallState {
  return options.runtime.readState({ installPath: options.installPath });
}

export async function runSetupGlobalInstall(
  options: RunSetupGlobalInstallOptions,
): Promise<SetupGlobalInstallResult> {
  try {
    await options.runtime.install();
    return { ok: true };
  } catch (err: unknown) {
    return {
      ok: false,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}
