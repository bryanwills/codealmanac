import path from "node:path";

import {
  CLAUDE_IMPORT_LINE,
  hasClaudeImportLine,
  removeClaudeImportLine,
} from "./instructions/claude.js";
import {
  codexInstructionBlockPresent,
  CODEX_INSTRUCTIONS_END,
  CODEX_INSTRUCTIONS_START,
} from "./instructions/codex.js";
import { readSetupInstructionGuides } from "./instructions/guides.js";
import {
  AGENT_INSTRUCTION_TARGETS,
  DEFAULT_INSTRUCTION_TARGETS,
  installInstructionTargets,
  missingInstructionTargets,
  removeInstructionTargets,
} from "./instructions/targets.js";
import type {
  AgentInstructionCheck,
  AgentInstructionDirs,
  AgentInstructionsChange,
  InstallAgentInstructionsOptions,
  InstructionTarget,
  InstructionTargetId,
} from "./instructions/types.js";
import type {
  SetupInstructionInstallRequest,
  SetupInstructionRuntime,
} from "../../shared/setup-instructions.js";
export { CLAUDE_IMPORT_LINE, hasClaudeImportLine, removeClaudeImportLine };
export {
  CODEX_INSTRUCTIONS_END,
  CODEX_INSTRUCTIONS_START,
  codexInstructionBlockPresent,
};
export {
  AGENT_INSTRUCTION_TARGETS,
  DEFAULT_INSTRUCTION_TARGETS,
  type AgentInstructionCheck,
  type AgentInstructionDirs,
  type AgentInstructionsChange,
  type InstallAgentInstructionsOptions,
  type InstructionTarget,
  type InstructionTargetId,
};

export function createPlatformSetupInstructionRuntime(): SetupInstructionRuntime {
  return {
    install: (request) => installAgentInstructions(platformInstallOptions(request)),
    remove: removeAgentInstructions,
  };
}

export async function installAgentInstructions(
  options: InstallAgentInstructionsOptions,
): Promise<AgentInstructionsChange> {
  const guides = await readSetupInstructionGuides(options.guidesDir);
  const targets = options.targets ?? DEFAULT_INSTRUCTION_TARGETS;
  const touched = await installInstructionTargets(targets, options, guides);

  return { anyChanges: touched.length > 0, filesTouched: touched };
}

export async function removeAgentInstructions(
  dirs: AgentInstructionDirs,
): Promise<AgentInstructionsChange> {
  const touched = await removeInstructionTargets(dirs);

  return { anyChanges: touched.length > 0, filesTouched: touched };
}

export async function checkAgentInstructions(
  dirs: AgentInstructionDirs,
): Promise<AgentInstructionCheck> {
  const missing = await missingInstructionTargets(dirs);

  return {
    ok: missing.length === 0,
    missing,
    message: missing.length === 0
      ? "Agent instructions installed"
      : `Agent instructions missing (${missing.join(", ")})`,
  };
}

function platformInstallOptions(
  request: SetupInstructionInstallRequest,
): InstallAgentInstructionsOptions {
  return {
    targets: request.targets,
    claudeDir: request.claudeDir ?? path.join(request.homeDir, ".claude"),
    codexDir: request.codexDir ?? path.join(request.homeDir, ".codex"),
    cursorDir: request.cursorDir ?? path.join(request.homeDir, ".cursor"),
    windsurfDir: request.windsurfDir ??
      path.join(request.homeDir, ".codeium", "windsurf"),
    opencodeDir: request.opencodeDir ??
      path.join(request.homeDir, ".config", "opencode"),
    guidesDir: request.guidesDir,
  };
}
