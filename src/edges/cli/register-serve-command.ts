import { Command } from "commander";

import { autoRegisterCurrentWikiIfNeeded } from "./autoregistration.js";
import { parsePositiveInt } from "./helpers.js";
import { waitForCliInterrupt } from "./interrupt.js";

export function registerServeCommand(program: Command): void {
  program
    .command("serve")
    .description("start the local read-only Almanac console")
    .option("--host <host>", "host to bind", "127.0.0.1")
    .option("--port <n>", "port to bind", parsePositiveInt, 3927)
    .action(async (opts: { host?: string; port?: number }) => {
      await autoRegisterCurrentWikiIfNeeded(process.cwd());
      const { runServe } = await import("./serve.js");
      await runServe({
        host: opts.host,
        port: opts.port,
        waitForStop: waitForCliInterrupt,
        write: (chunk) => {
          process.stdout.write(chunk);
        },
      });
    });
}
