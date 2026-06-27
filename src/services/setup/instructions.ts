import { existsSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  AGENT_INSTRUCTION_TARGETS,
  CLAUDE_IMPORT_LINE,
  hasClaudeImportLine,
  installAgentInstructions,
  type InstructionTarget,
} from "../../agent/install-targets.js";
import {
  CODEX_INSTRUCTIONS_END,
  CODEX_INSTRUCTIONS_START,
  hasCodexInstructions,
} from "../../agent/instructions/codex.js";

export type SetupInstructionTargetId =
  | "claude"
  | "codex"
  | "cursor"
  | "windsurf"
  | "opencode";

export interface SetupInstructionTarget {
  id: SetupInstructionTargetId;
  displayName: string;
}

export interface SetupInstructionsChange {
  anyChanges: boolean;
  filesTouched: string[];
}

export const SETUP_IMPORT_LINE = CLAUDE_IMPORT_LINE;

export {
  CODEX_INSTRUCTIONS_END,
  CODEX_INSTRUCTIONS_START,
  hasCodexInstructions,
};

export const SETUP_INSTRUCTION_TARGETS: readonly SetupInstructionTarget[] =
  AGENT_INSTRUCTION_TARGETS.map(setupInstructionTargetFromAgentTarget);

export const DEFAULT_SETUP_INSTRUCTION_TARGETS:
  readonly SetupInstructionTargetId[] = SETUP_INSTRUCTION_TARGETS.map(
    (target) => target.id,
  );

export interface InstallSetupInstructionsOptions {
  targets: readonly SetupInstructionTargetId[];
  claudeDir?: string;
  codexDir?: string;
  cursorDir?: string;
  windsurfDir?: string;
  opencodeDir?: string;
  guidesDir?: string;
  homeDir: string;
}

export async function installSetupInstructions(
  options: InstallSetupInstructionsOptions,
): Promise<SetupInstructionsChange> {
  const change = await installAgentInstructions({
    targets: options.targets,
    claudeDir: options.claudeDir ?? path.join(options.homeDir, ".claude"),
    codexDir: options.codexDir ?? path.join(options.homeDir, ".codex"),
    cursorDir: options.cursorDir ?? path.join(options.homeDir, ".cursor"),
    windsurfDir: options.windsurfDir ?? path.join(options.homeDir, ".codeium", "windsurf"),
    opencodeDir: options.opencodeDir ?? path.join(options.homeDir, ".config", "opencode"),
    guidesDir: options.guidesDir ?? resolveSetupGuidesDir(),
  });
  return {
    anyChanges: change.anyChanges,
    filesTouched: change.filesTouched,
  };
}

export function hasSetupImportLine(contents: string): boolean {
  return hasClaudeImportLine(contents);
}

/**
 * Locate `guides/` relative to the installed package. Mirrors
 * `resolvePromptsDir` from `src/agent/prompts.ts`.
 */
export function resolveSetupGuidesDir(): string {
  const here = path.dirname(fileURLToPath(import.meta.url));
  const candidates = [
    path.resolve(here, "..", "guides"), // dist layout
    path.resolve(here, "..", "..", "guides"), // src layout
    path.resolve(here, "..", "..", "..", "guides"),
  ];
  for (const dir of candidates) {
    if (looksLikeGuidesDir(dir)) return dir;
  }
  try {
    const require = createRequire(import.meta.url);
    const pkgJson = require.resolve("codealmanac/package.json");
    const guides = path.join(path.dirname(pkgJson), "guides");
    if (looksLikeGuidesDir(guides)) return guides;
  } catch {
    // Fall through to the detailed error below.
  }
  throw new Error(
    "could not locate bundled guides/ directory. Tried:\n" +
      candidates.map((c) => `  - ${c}`).join("\n"),
  );
}

function looksLikeGuidesDir(dir: string): boolean {
  return existsSync(path.join(dir, "mini.md"));
}

function setupInstructionTargetFromAgentTarget(
  target: InstructionTarget,
): SetupInstructionTarget {
  return {
    id: target.id,
    displayName: target.displayName,
  };
}
