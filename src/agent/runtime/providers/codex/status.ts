import {
  commandExists,
  runStatusCommand,
} from "../../../../platform/agent-cli-status.js";

export const defaultCommandExists = commandExists;

export function defaultJobStatus(
  command: string,
  args: string[],
): Promise<{ ok: boolean; detail: string }> {
  return runStatusCommand(command, args, { timeoutMs: null });
}
