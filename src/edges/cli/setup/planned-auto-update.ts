import type { SetupTheme } from "./output.js";
import {
  type GlobalInstallStepResult,
} from "./global-install-step.js";
import {
  runAutoUpdateSetupStep,
  skipAutoUpdateSetupStep,
} from "./auto-update-step.js";
import {
  setupFailure,
  type SetupStepResult,
} from "./setup-flow-result.js";
import type { SetupOptions } from "./types.js";

export async function runPlannedAutoUpdate(args: {
  options: SetupOptions;
  out: NodeJS.WritableStream;
  theme: SetupTheme;
  cliAutoUpdate: boolean;
  globalInstall: GlobalInstallStepResult;
}): Promise<SetupStepResult> {
  if (!args.cliAutoUpdate) return { ok: true };
  if (args.globalInstall.ephemeral && !args.globalInstall.durableGlobalInstall) {
    skipAutoUpdateSetupStep(args.out, args.theme);
    return { ok: true };
  }
  const update = await runAutoUpdateSetupStep({
    out: args.out,
    theme: args.theme,
    options: {
      cwd: args.options.cwd,
      homeDir: args.options.homeDir,
      pathEnvironment: args.options.pathEnvironment,
      cliProgramArguments: args.options.cliProgramArguments,
      autoUpdateEvery: args.options.autoUpdateEvery,
      updatePlistPath: args.options.updatePlistPath,
      updateProgramArguments: args.globalInstall.ephemeral
        ? globalUpdateProgramArguments()
        : undefined,
      automationExec: args.options.automationExec,
    },
  });
  if (!update.ok) return setupFailure(update.stderr, update.exitCode);
  return { ok: true };
}

function globalUpdateProgramArguments(): string[] {
  return ["/usr/bin/env", "almanac", "update"];
}
