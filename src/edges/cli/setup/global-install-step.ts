import {
  readSetupGlobalInstallState,
  runSetupGlobalInstall,
  type SetupGlobalInstallRuntime,
} from "../../../services/setup/index.js";
import { createPlatformSetupGlobalInstallRuntime } from "../../../platform/setup/runtime.js";
import {
  confirm,
  type InstallDecision,
} from "./line-prompt.js";
import {
  type SetupTheme,
  dim,
  stepActive,
  stepDone,
  stepSkipped,
  writeSetupDivider,
} from "./output.js";
import type { SetupInputStream } from "./types.js";

export interface GlobalInstallStepOptions {
  installPath?: string | null;
  spawnGlobalInstall?: () => Promise<void>;
  globalInstallRuntime?: SetupGlobalInstallRuntime;
}

export interface GlobalInstallStepResult {
  ephemeral: boolean;
  durableGlobalInstall: boolean;
}

export async function runGlobalInstallStep(args: {
  input: SetupInputStream;
  out: NodeJS.WritableStream;
  theme: SetupTheme;
  interactive: boolean;
  options: GlobalInstallStepOptions;
}): Promise<GlobalInstallStepResult> {
  const runtime = args.options.globalInstallRuntime ??
    createPlatformSetupGlobalInstallRuntime({
      spawnGlobalInstall: args.options.spawnGlobalInstall,
    });
  const { ephemeral } = readSetupGlobalInstallState({
    installPath: args.options.installPath,
    runtime,
  });
  let durableGlobalInstall = false;
  if (!ephemeral) {
    return { ephemeral, durableGlobalInstall };
  }

  let globalAction: InstallDecision = "install";
  if (args.interactive) {
    globalAction = await confirm(
      args.input,
      args.out,
      args.theme,
      `Running from an ephemeral npx location. Install globally so 'almanac' stays on PATH?`,
      true,
    );
  }
  if (globalAction === "install") {
    stepActive(args.out, args.theme, "Installing Almanac package globally...");
    const install = await runSetupGlobalInstall({
      runtime,
    });
    if (install.ok) {
      durableGlobalInstall = true;
      stepDone(
        args.out,
        args.theme,
        "Almanac installed globally (almanac now on PATH)",
      );
    } else {
      stepActive(args.out, args.theme, `Global install failed: ${install.error}`);
      args.out.write(
        `  ${dim(args.theme, "You can retry manually: npm install -g codealmanac")}\n`,
      );
    }
  } else {
    stepSkipped(
      args.out,
      args.theme,
      `Global install ${dim(
        args.theme,
        "skipped — almanac will not be on PATH after this session",
      )}`,
    );
  }
  writeSetupDivider(args.out, args.theme);
  return { ephemeral, durableGlobalInstall };
}
