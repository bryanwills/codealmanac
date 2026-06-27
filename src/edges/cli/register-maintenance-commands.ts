import { Command } from "commander";

import { autoRegisterIfNeeded } from "../../services/wiki/autoregistration.js";

export function registerMaintenanceCommands(program: Command): void {
  program
    .command("reindex")
    .description("force a full rebuild of .almanac/index.db")
    .option("--wiki <name>", "target a specific registered wiki")
    .action(async (opts: { wiki?: string }) => {
      await autoRegisterIfNeeded(process.cwd());
      const { runReindex } = await import("../../cli/commands/reindex.js");
      const result = await runReindex({
        cwd: process.cwd(),
        wiki: opts.wiki,
      });
      process.stdout.write(result.stdout);
      if (result.exitCode !== 0) process.exitCode = result.exitCode;
    });
}
