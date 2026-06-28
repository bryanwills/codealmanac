import type { SetupOptions, SetupResult } from "./types.js";
import type { SetupTheme } from "./output.js";
import {
  stepDone,
  whiteBold,
  writeSetupDivider,
} from "./output.js";
import { chooseDefaultAgent } from "./agent-choice.js";
import { runAutoCommitSetupStep } from "./auto-commit-step.js";
import {
  runAutoUpdateSetupStep,
  skipAutoUpdateSetupStep,
} from "./auto-update-step.js";
import { runAutomationSetupStep } from "./automation-step.js";
import {
  type GlobalInstallStepResult,
  runGlobalInstallStep,
} from "./global-install-step.js";
import { runGuidesSetupStep } from "./guides-step.js";
import { buildSetupPlan } from "./setup-plan.js";

export type SetupNextStepsMode = "hosted" | "self-managed";

export type SetupFlowResult =
  | { ok: true; nextStepsMode: SetupNextStepsMode }
  | SetupFailure;

type SetupStepResult =
  | { ok: true }
  | SetupFailure;

interface SetupFailure {
  ok: false;
  result: SetupResult;
}

export async function runSetupFlow(args: {
  options: SetupOptions;
  out: NodeJS.WritableStream;
  theme: SetupTheme;
  interactive: boolean;
}): Promise<SetupFlowResult> {
  const plan = await buildSetupPlan(args);
  const nextStepsMode = plan.selfManagedAutomation ? "self-managed" : "hosted";
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
    selfManagedAutomation: plan.selfManagedAutomation,
    autoCommit: plan.autoCommit,
  });

  return { ok: true, nextStepsMode };
}

async function runPlannedAutoUpdate(args: {
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

async function runSelfManagedAutomation(args: {
  options: SetupOptions;
  out: NodeJS.WritableStream;
  theme: SetupTheme;
  interactive: boolean;
  globalInstall: GlobalInstallStepResult;
}): Promise<SetupStepResult> {
  const agentChoice = await chooseDefaultAgent({
    input: args.options.stdin,
    out: args.out,
    theme: args.theme,
    interactive: args.interactive,
    requested: args.options.agent,
    requestedModel: args.options.model,
    readinessRuntime: requireAgentReadinessRuntime(args.options),
    spawnCli: args.options.spawnCli,
    runProviderFixCommand: requireSetupProviderFixCommand(args.options),
    environment: args.options.environment,
  });
  if (!agentChoice.ok) {
    return setupFailure(`almanac: ${agentChoice.error}\n`, 1);
  }
  stepDone(
    args.out,
    args.theme,
    `Agent: ${whiteBold(args.theme, agentChoice.provider)}` +
      ` (${agentChoice.model ?? "provider default"})`,
  );
  writeSetupDivider(args.out, args.theme);

  const automation = await runAutomationSetupStep({
    out: args.out,
    theme: args.theme,
    interactive: args.interactive,
    options: { ...args.options, cwd: args.options.cwd },
    ephemeral: args.globalInstall.ephemeral,
    durableGlobalInstall: args.globalInstall.durableGlobalInstall,
  });
  if (!automation.ok) {
    return setupFailure(automation.stderr, automation.exitCode);
  }
  return { ok: true };
}

async function runPlannedAutoCommit(args: {
  out: NodeJS.WritableStream;
  theme: SetupTheme;
  interactive: boolean;
  selfManagedAutomation: boolean;
  autoCommit: boolean;
  options: SetupOptions;
}): Promise<void> {
  if (
    args.selfManagedAutomation ||
    args.autoCommit ||
    args.options.autoCommit === false
  ) {
    await runAutoCommitSetupStep({
      out: args.out,
      theme: args.theme,
      interactive: args.interactive,
      options: { autoCommit: args.autoCommit },
    });
  } else if (args.autoCommit === false) {
    await runAutoCommitSetupStep({
      out: args.out,
      theme: args.theme,
      interactive: false,
      options: { autoCommit: false },
    });
  }
}

function setupFailure(stderr: string, exitCode: number): SetupFailure {
  return {
    ok: false,
    result: { stdout: "", stderr, exitCode },
  };
}

function globalUpdateProgramArguments(): string[] {
  return ["/usr/bin/env", "almanac", "update"];
}

function requireAgentReadinessRuntime(
  options: SetupOptions,
): NonNullable<SetupOptions["agentReadinessRuntime"]> {
  if (options.agentReadinessRuntime === undefined) {
    throw new Error("setup requires an agent readiness runtime");
  }
  return options.agentReadinessRuntime;
}

function requireSetupProviderFixCommand(
  options: SetupOptions,
): NonNullable<SetupOptions["runProviderFixCommand"]> {
  if (options.runProviderFixCommand === undefined) {
    throw new Error("setup requires a provider fix-command runner");
  }
  return options.runProviderFixCommand;
}
