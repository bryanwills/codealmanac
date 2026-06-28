import { Command } from "commander";

import { registerAutomationInstallCommand } from "./register-automation-install-command.js";
import { registerAutomationStatusCommand } from "./register-automation-status-command.js";
import { registerAutomationUninstallCommand } from "./register-automation-uninstall-command.js";

export function registerAutomationCommands(program: Command): void {
  const automation = program
    .command("automation")
    .description("manage scheduled Almanac automation");

  registerAutomationInstallCommand(automation);
  registerAutomationUninstallCommand(automation);
  registerAutomationStatusCommand(automation);
}
