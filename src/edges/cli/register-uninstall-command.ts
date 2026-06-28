import { Command } from "commander";
import { homedir } from "node:os";

import { emit, shouldUseStdoutColor } from "./helpers.js";

export function registerUninstallCommand(program: Command): void {
  program
    .command("uninstall")
    .description("remove automation + guides + import line")
    .option("-y, --yes", "skip confirmations; remove everything")
    .option(
      "--keep-automation",
      "don't remove the scheduler (guides still prompted unless --yes)",
    )
    .option(
      "--keep-guides",
      "don't remove the guides or CLAUDE.md import (scheduler still prompted unless --yes)",
    )
    .action(
      async (opts: {
        yes?: boolean;
        keepAutomation?: boolean;
        keepGuides?: boolean;
      }) => {
        const { runUninstall } = await import("./uninstall.js");
        const result = await runUninstall({
          yes: opts.yes,
          keepAutomation: opts.keepAutomation,
          keepGuides: opts.keepGuides,
          homeDir: homedir(),
          isTTY: process.stdin.isTTY === true,
          stdin: process.stdin,
          stdout: process.stdout,
          color: shouldUseStdoutColor(),
        });
        emit(result);
      },
    );
}
