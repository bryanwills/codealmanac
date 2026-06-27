import { Command } from "commander";

import { registerAgentCommands } from "./register-agent-commands.js";
import { registerAutomationCommands } from "./register-automation-commands.js";
import { registerConfigCommands } from "./register-config-commands.js";
import { registerEditCommands } from "./register-edit-commands.js";
import { registerJobsCommands } from "./register-jobs-commands.js";
import {
  registerGardenCommand,
  registerLifecycleRunCommands,
} from "./register-lifecycle-run-commands.js";
import { registerMaintenanceCommands } from "./register-maintenance-commands.js";
import { registerQueryCommands } from "./register-query-commands.js";
import {
  registerSetupCommands,
  type SetupCommandDeps,
} from "./register-setup-commands.js";
import { registerSyncCommands } from "./register-sync-commands.js";

export interface RegisterCommandDeps extends SetupCommandDeps {}

export function registerCommands(
  program: Command,
  deps: RegisterCommandDeps = {},
): void {
  registerQueryCommands(program);
  registerEditCommands(program);
  registerLifecycleRunCommands(program);
  registerSyncCommands(program);
  registerGardenCommand(program);
  registerJobsCommands(program);
  registerAutomationCommands(program);
  registerMaintenanceCommands(program);
  registerAgentCommands(program);
  registerConfigCommands(program);
  registerSetupCommands(program, deps);
}
