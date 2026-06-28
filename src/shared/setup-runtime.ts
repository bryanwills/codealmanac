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

export type SetupProviderFixCommandResult =
  | { ok: true }
  | { ok: false; error: string };

export type SetupProviderFixCommandRunner = (
  command: string,
) => Promise<SetupProviderFixCommandResult>;
