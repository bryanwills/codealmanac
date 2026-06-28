import { Command } from "commander";

import { registerHealthCommand } from "./register-health-command.js";
import { registerListCommand } from "./register-list-command.js";
import { registerSearchCommand } from "./register-search-command.js";
import { registerServeCommand } from "./register-serve-command.js";
import { registerShowCommand } from "./register-show-command.js";

export { resolveSearchOutputMode } from "./register-search-command.js";

export function registerQueryCommands(program: Command): void {
  registerServeCommand(program);
  registerSearchCommand(program);
  registerShowCommand(program);
  registerHealthCommand(program);
  registerListCommand(program);
}
