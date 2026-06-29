import { homedir } from "node:os";
import path from "node:path";

import {
  installAgentInstructions,
  type InstructionTargetId,
} from "../../../agent/install-targets.js";
import {
  BAR,
  DIM,
  RST,
  stepDone,
  stepSkipped,
} from "./output.js";
import { resolveGuidesDir } from "./guides.js";

export interface GuidesSetupStepOptions {
  skipGuides?: boolean;
  claudeDir?: string;
  codexDir?: string;
  cursorDir?: string;
  windsurfDir?: string;
  opencodeDir?: string;
  guidesDir?: string;
}

export type GuidesSetupStepResult =
  | { ok: true }
  | { ok: false; stderr: string; exitCode: number };

export async function runGuidesSetupStep(args: {
  out: NodeJS.WritableStream;
  options: GuidesSetupStepOptions;
  targets: readonly InstructionTargetId[];
}): Promise<GuidesSetupStepResult> {
  if (args.options.skipGuides === true || args.targets.length === 0) {
    stepSkipped(args.out, `Agent instructions ${DIM}skipped${RST}`);
    args.out.write(BAR + "\n");
    return { ok: true };
  }

  try {
    const summary = await installAgentInstructions({
      targets: args.targets,
      claudeDir: args.options.claudeDir ?? path.join(homedir(), ".claude"),
      codexDir: args.options.codexDir ?? path.join(homedir(), ".codex"),
      cursorDir: args.options.cursorDir ?? path.join(homedir(), ".cursor"),
      windsurfDir: args.options.windsurfDir ?? path.join(homedir(), ".codeium", "windsurf"),
      opencodeDir: args.options.opencodeDir ?? path.join(homedir(), ".config", "opencode"),
      guidesDir: args.options.guidesDir ?? resolveGuidesDir(),
    });
    const guidesSummary = summary.anyChanges
      ? "Agent instructions added"
      : `Agent instructions ${DIM}already added${RST}`;
    stepDone(args.out, guidesSummary);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return {
      ok: false,
      stderr: `almanac: guide install failed: ${msg}\n`,
      exitCode: 1,
    };
  }
  args.out.write(BAR + "\n");
  return { ok: true };
}
