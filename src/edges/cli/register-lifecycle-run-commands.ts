import { Command } from "commander";

import {
  registerAbsorbCommand,
  registerIngestCommand,
} from "./register-absorb-command.js";
import { registerInitCommand } from "./register-init-command.js";

export { registerGardenCommand } from "./register-garden-command.js";

export function registerLifecycleRunCommands(program: Command): void {
  registerInitCommand(program);
  registerAbsorbCommand(program);
  registerIngestCommand(program);
}
