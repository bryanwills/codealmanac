import { applySetupAutoCommit } from "../../../services/setup/index.js";
import {
  BAR,
  DIM,
  RST,
  stepDone,
  stepSkipped,
} from "./output.js";

export interface AutoCommitSetupStepOptions {
  autoCommit?: boolean;
}

export async function runAutoCommitSetupStep(args: {
  out: NodeJS.WritableStream;
  interactive: boolean;
  options: AutoCommitSetupStepOptions;
}): Promise<void> {
  const result = await applySetupAutoCommit({
    autoCommit: args.options.autoCommit,
  });
  if (result.enabled) {
    stepDone(args.out, "Auto-commit enabled");
  } else {
    stepSkipped(args.out, `Auto-commit ${DIM}disabled${RST}`);
  }
  args.out.write(BAR + "\n");
}
