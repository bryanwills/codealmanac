import type { SetupNextStepsMode } from "../../../services/setup/index.js";
import type { SetupResult } from "./types.js";

export type SetupFlowResult =
  | { ok: true; nextStepsMode: SetupNextStepsMode }
  | SetupFailure;

export type SetupStepResult =
  | { ok: true }
  | SetupFailure;

export interface SetupFailure {
  ok: false;
  result: SetupResult;
}

export function setupFailure(stderr: string, exitCode: number): SetupFailure {
  return {
    ok: false,
    result: { stdout: "", stderr, exitCode },
  };
}
