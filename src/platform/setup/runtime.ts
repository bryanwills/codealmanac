import {
  detectCurrentInstallPath,
  detectEphemeral,
  spawnGlobalInstall,
} from "../install/global-package.js";
import { runInheritedShellCommand } from "../shell.js";
import type {
  SetupGlobalInstallRuntime,
  SetupGlobalInstallStateOptions,
  SetupProviderFixCommandRunner,
} from "../../shared/setup-runtime.js";

export function createPlatformSetupGlobalInstallRuntime(options: {
  spawnGlobalInstall?: () => Promise<void>;
} = {}): SetupGlobalInstallRuntime {
  return {
    readState: (stateOptions?: SetupGlobalInstallStateOptions) => ({
      ephemeral: setupInstallPathIsEphemeral(stateOptions),
    }),
    install: () => (options.spawnGlobalInstall ?? spawnGlobalInstall)(),
  };
}

export const runPlatformSetupProviderFixCommand: SetupProviderFixCommandRunner =
  runInheritedShellCommand;

function setupInstallPathIsEphemeral(
  options: SetupGlobalInstallStateOptions = {},
): boolean {
  if (options.installPath !== undefined) {
    return options.installPath !== null && detectEphemeral(options.installPath);
  }
  return detectEphemeral(detectCurrentInstallPath());
}
