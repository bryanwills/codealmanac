import { Command } from "commander";

import {
  registerDoctorCommand,
  type RegisterDoctorCommandDeps,
} from "./register-doctor-command.js";
import {
  registerSetupCommand,
  type RegisterSetupCommandDeps,
} from "./register-setup-command.js";
import { registerUninstallCommand } from "./register-uninstall-command.js";
import { registerUpdateCommand } from "./register-update-command.js";

export interface SetupCommandDeps
  extends RegisterSetupCommandDeps, RegisterDoctorCommandDeps {}

export function registerSetupCommands(
  program: Command,
  deps: SetupCommandDeps = {},
): void {
  registerSetupCommand(program, deps);
  registerDoctorCommand(program, deps);
  registerUpdateCommand(program);
  registerUninstallCommand(program);
}
