export type SetupProviderFixCommandResult =
  | { ok: true }
  | { ok: false; error: string };

export type SetupProviderFixCommandRunner = (
  command: string,
) => Promise<SetupProviderFixCommandResult>;

export function normalizeSetupProviderFixCommand(
  fixCommand: string | null,
): string | null {
  if (fixCommand === null) return null;
  return fixCommand.startsWith("run: ")
    ? fixCommand.slice("run: ".length)
    : fixCommand;
}

export function runnableSetupProviderFixCommand(
  fixCommand: string | null,
): string | null {
  if (fixCommand?.startsWith("run: ") !== true) return null;
  return fixCommand.slice("run: ".length);
}

export function runSetupProviderFixCommand(
  command: string,
  runner: SetupProviderFixCommandRunner,
): Promise<SetupProviderFixCommandResult> {
  return runner(command);
}
