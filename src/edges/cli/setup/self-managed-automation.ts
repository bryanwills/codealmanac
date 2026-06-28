import { chooseDefaultAgent } from "./agent-choice.js";
import { runAutomationSetupStep } from "./automation-step.js";
import type {
  GlobalInstallStepResult,
} from "./global-install-step.js";
import {
  stepDone,
  whiteBold,
  writeSetupDivider,
  type SetupTheme,
} from "./output.js";
import {
  setupFailure,
  type SetupStepResult,
} from "./setup-flow-result.js";
import type { SetupOptions } from "./types.js";

export async function runSelfManagedAutomation(args: {
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
