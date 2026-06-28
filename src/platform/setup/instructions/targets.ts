import {
  DEFAULT_SETUP_INSTRUCTION_TARGETS,
  SETUP_INSTRUCTION_TARGETS,
} from "../../../shared/setup-instructions.js";
import {
  claudeInstructionsPresent,
  ensureClaudeInstructions,
  removeClaudeInstructions,
} from "./claude.js";
import {
  codexInstructionBlockPresent,
  ensureCodexInstructions,
  removeCodexInstructions,
} from "./codex.js";
import {
  cursorInstructionsPresent,
  ensureCursorInstructions,
  removeCursorInstructions,
} from "./cursor.js";
import {
  ensureOpenCodeInstructions,
  openCodeInstructionsPresent,
  removeOpenCodeInstructions,
} from "./opencode.js";
import type { SetupInstructionGuides } from "./guides.js";
import type {
  AgentInstructionDirs,
  InstructionTarget,
  InstructionTargetId,
} from "./types.js";
import {
  ensureWindsurfInstructions,
  removeWindsurfInstructions,
  windsurfInstructionsPresent,
} from "./windsurf.js";

export const AGENT_INSTRUCTION_TARGETS: readonly InstructionTarget[] =
  SETUP_INSTRUCTION_TARGETS;

export const DEFAULT_INSTRUCTION_TARGETS: readonly InstructionTargetId[] =
  DEFAULT_SETUP_INSTRUCTION_TARGETS;

export async function installInstructionTargets(
  targets: readonly InstructionTargetId[],
  dirs: AgentInstructionDirs,
  guides: SetupInstructionGuides,
): Promise<string[]> {
  const touched: string[] = [];
  for (const target of targets) {
    touched.push(...await installInstructionTarget(target, dirs, guides));
  }
  return touched;
}

export async function removeInstructionTargets(
  dirs: AgentInstructionDirs,
): Promise<string[]> {
  return [
    ...await removeClaudeInstructions(dirs.claudeDir),
    ...await removeCodexInstructions(dirs.codexDir),
    ...await removeCursorInstructions(dirs.cursorDir),
    ...await removeWindsurfInstructions(dirs.windsurfDir),
    ...await removeOpenCodeInstructions(dirs.opencodeDir),
  ];
}

export async function missingInstructionTargets(
  dirs: AgentInstructionDirs,
): Promise<string[]> {
  return [
    ...await claudeInstructionsPresent(dirs.claudeDir),
    ...await codexInstructionsMissing(dirs.codexDir),
    ...cursorInstructionsPresent(dirs.cursorDir),
    ...await windsurfInstructionsPresent(dirs.windsurfDir),
    ...await openCodeInstructionsPresent(dirs.opencodeDir),
  ];
}

async function installInstructionTarget(
  target: InstructionTargetId,
  dirs: AgentInstructionDirs,
  guides: SetupInstructionGuides,
): Promise<string[]> {
  switch (target) {
    case "claude":
      return await ensureClaudeInstructions({
        claudeDir: dirs.claudeDir,
        miniGuidePath: guides.miniGuidePath,
        referenceGuidePath: guides.referenceGuidePath,
      });
    case "codex":
      return await ensureCodexInstructions(dirs.codexDir, guides.miniContents)
        ? ["AGENTS.md"]
        : [];
    case "cursor":
      return await ensureCursorInstructions(dirs.cursorDir, guides.miniContents);
    case "windsurf":
      return await ensureWindsurfInstructions(
        dirs.windsurfDir,
        guides.miniContents,
      );
    case "opencode":
      return await ensureOpenCodeInstructions(
        dirs.opencodeDir,
        guides.miniContents,
      );
    default: {
      const exhaustive: never = target;
      throw new Error(`unknown instruction target: ${exhaustive}`);
    }
  }
}

async function codexInstructionsMissing(codexDir: string): Promise<string[]> {
  if (await codexInstructionBlockPresent(codexDir)) return [];
  return ["Codex AGENTS.md instructions"];
}
