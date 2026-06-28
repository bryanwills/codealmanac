import type { SetupOptions } from "./types.js";
import type { SetupTheme } from "./output.js";
import { runAutoCommitSetupStep } from "./auto-commit-step.js";
import { runGlobalInstallStep } from "./global-install-step.js";
import { runGuidesSetupStep } from "./guides-step.js";
import { runPlannedAutoUpdate } from "./planned-auto-update.js";
import { runSelfManagedAutomation } from "./self-managed-automation.js";
import { buildSetupPlan } from "./setup-plan.js";
import {
  setupFailure,
  type SetupFlowResult,
} from "./setup-flow-result.js";

export async function runSetupFlow(args: {
  options: SetupOptions;
  out: NodeJS.WritableStream;
  theme: SetupTheme;
  interactive: boolean;
}): Promise<SetupFlowResult> {
  const plan = await buildSetupPlan(args);
  const guides = await runGuidesSetupStep({
    out: args.out,
    theme: args.theme,
    options: args.options,
    targets: plan.instructionTargets,
  });
  if (!guides.ok) {
    return setupFailure(guides.stderr, guides.exitCode);
  }

  const globalInstall = await runGlobalInstallStep({
    input: args.options.stdin,
    out: args.out,
    theme: args.theme,
    interactive: args.interactive,
    options: args.options,
  });

  const autoUpdate = await runPlannedAutoUpdate({
    ...args,
    cliAutoUpdate: plan.cliAutoUpdate,
    globalInstall,
  });
  if (!autoUpdate.ok) return { ok: false, result: autoUpdate.result };

  if (plan.selfManagedAutomation) {
    const automation = await runSelfManagedAutomation({
      ...args,
      globalInstall,
    });
    if (!automation.ok) return { ok: false, result: automation.result };
  }

  await runPlannedAutoCommit({
    ...args,
    autoCommit: plan.autoCommit,
  });

  return { ok: true, nextStepsMode: plan.nextStepsMode };
}

async function runPlannedAutoCommit(args: {
  out: NodeJS.WritableStream;
  theme: SetupTheme;
  interactive: boolean;
  autoCommit: boolean;
}): Promise<void> {
  await runAutoCommitSetupStep({
    out: args.out,
    theme: args.theme,
    interactive: args.interactive,
    options: { autoCommit: args.autoCommit },
  });
}
