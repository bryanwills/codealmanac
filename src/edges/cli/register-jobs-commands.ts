import { Command } from "commander";

import { registerJobCancelCommand } from "./register-job-cancel-command.js";
import { registerJobLogCommands } from "./register-job-log-commands.js";
import { registerJobReadCommands } from "./register-job-read-commands.js";

export function registerJobsCommands(program: Command): void {
  const jobs = program
    .command("jobs")
    .description("show and manage Almanac background jobs");

  registerJobReadCommands(jobs);
  registerJobLogCommands(jobs);
  registerJobCancelCommand(jobs);
}
