import { runAutomationInstall } from "../automation.js";
import {
  type SetupTheme,
  dim,
  stepActive,
  stepDone,
  stepSkipped,
  writeSetupDivider,
} from "./output.js";
import type { AutomationExecFn } from "./types.js";

export interface AutoUpdateSetupStepOptions {
  autoUpdateEvery?: string;
  updatePlistPath?: string;
  updateProgramArguments?: string[];
  automationExec?: AutomationExecFn;
}

export type AutoUpdateSetupStepResult =
  | { ok: true }
  | { ok: false; stderr: string; exitCode: number };

export async function runAutoUpdateSetupStep(args: {
  out: NodeJS.WritableStream;
  theme: SetupTheme;
  options: AutoUpdateSetupStepOptions;
}): Promise<AutoUpdateSetupStepResult> {
  const update = await runAutomationInstall({
    tasks: ["update"],
    every: args.options.autoUpdateEvery,
    updateProgramArguments: args.options.updateProgramArguments,
    updatePlistPath: args.options.updatePlistPath,
    exec: args.options.automationExec,
  });
  if (update.exitCode !== 0) {
    stepActive(
      args.out,
      args.theme,
      `Auto-update automation: ${update.stderr.trim()}`,
    );
    return {
      ok: false,
      stderr: update.stderr,
      exitCode: update.exitCode,
    };
  }
  stepDone(args.out, args.theme, "Auto-update automation installed");
  writeSetupDivider(args.out, args.theme);
  return { ok: true };
}

export function skipAutoUpdateSetupStep(
  out: NodeJS.WritableStream,
  theme: SetupTheme,
): void {
  stepSkipped(
    out,
    theme,
    `Auto-update automation ${dim(theme, "skipped")}`,
  );
  writeSetupDivider(out, theme);
}
