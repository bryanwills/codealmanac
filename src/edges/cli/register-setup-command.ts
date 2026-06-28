import { Command } from "commander";
import { homedir } from "node:os";

import { currentCliProgramArguments } from "./current-cli.js";
import { emit, shouldUseStdoutColor } from "./helpers.js";
import { createAgentReadinessRuntime } from "../../app/agent-readiness-runtime.js";
import { resolveBundledGuidesDir } from "../../platform/install/guides.js";

export interface RegisterSetupCommandDeps {
  runSetup?: typeof import("./setup/index.js").runSetup;
}

export function registerSetupCommand(
  program: Command,
  deps: RegisterSetupCommandDeps = {},
): void {
  program
    .command("setup")
    .description("set up local Almanac access")
    .option("-y, --yes", "skip prompts; use setup defaults")
    .option("--agent <agent>", "default agent: claude, codex, or cursor")
    .option("--model <model>", "default model for the selected agent")
    .option("--skip-automation", "skip scheduled setup tasks")
    .option("--sync-every <duration>", "scheduled sync interval (default: 5h)")
    .option("--sync-quiet <duration>", "scheduled sync quiet window (default: 45m)")
    .option("--garden-every <duration>", "scheduled Garden interval (default: 4h)")
    .option("--garden-off", "disable scheduled Garden automation")
    .option("--auto-update", "install scheduled Almanac self-update")
    .option("--auto-update-every <duration>", "scheduled self-update interval (default: 1d)")
    .option("--skip-guides", "opt out of the CLAUDE.md guides")
    .option("--auto-commit", "allow Almanac lifecycle runs to commit wiki source changes")
    .option("--no-auto-commit", "leave lifecycle wiki changes in the working tree")
    .action(
      async (opts: {
        yes?: boolean;
        agent?: string;
        model?: string;
        skipAutomation?: boolean;
        syncEvery?: string;
        syncQuiet?: string;
        gardenEvery?: string;
        gardenOff?: boolean;
        autoUpdate?: boolean;
        autoUpdateEvery?: string;
        skipGuides?: boolean;
        autoCommit?: boolean;
      }) => {
        const runSetup = deps.runSetup ??
          (await import("./setup/index.js")).runSetup;
        const result = await runSetup({
          yes: opts.yes,
          agent: opts.agent,
          model: opts.model,
          skipAutomation: opts.skipAutomation,
          automationEvery: opts.syncEvery,
          automationQuiet: opts.syncQuiet,
          gardenEvery: opts.gardenEvery,
          gardenOff: opts.gardenOff,
          autoUpdate: opts.autoUpdate,
          autoUpdateEvery: opts.autoUpdateEvery,
          skipGuides: opts.skipGuides,
          autoCommit: opts.autoCommit,
          cwd: process.cwd(),
          homeDir: homedir(),
          pathEnvironment: process.env.PATH,
          environment: process.env,
          agentReadinessRuntime: createAgentReadinessRuntime(),
          cliProgramArguments: currentCliProgramArguments(),
          isTTY: process.stdin.isTTY === true,
          stdin: process.stdin,
          stdout: process.stdout,
          color: shouldUseStdoutColor(),
          guidesDir: opts.skipGuides === true
            ? undefined
            : resolveBundledGuidesDir(),
        });
        emit(result);
      },
    );
}
