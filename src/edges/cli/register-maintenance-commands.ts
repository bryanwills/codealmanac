import { Command } from "commander";

import { emit, emitCliWarning } from "./helpers.js";
import { autoRegisterCurrentWikiIfNeeded } from "./autoregistration.js";

export function registerMaintenanceCommands(program: Command): void {
  program
    .command("reindex")
    .description("force a full rebuild of .almanac/index.db")
    .option("--wiki <name>", "target a specific registered wiki")
    .action(async (opts: { wiki?: string }) => {
      await autoRegisterCurrentWikiIfNeeded(process.cwd());
      const { runReindex } = await import("./commands/reindex.js");
      const result = await runReindex({
        cwd: process.cwd(),
        wiki: opts.wiki,
        warnings: emitCliWarning,
      });
      emit(result);
    });
}
