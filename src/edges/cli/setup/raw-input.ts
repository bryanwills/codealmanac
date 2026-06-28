import type { SetupInputStream } from "./types.js";

export function canUseRawInput(input: SetupInputStream): boolean {
  return input.isTTY === true && typeof input.setRawMode === "function";
}
