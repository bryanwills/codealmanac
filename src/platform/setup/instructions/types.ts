import type {
  SetupInstructionDirs,
  SetupInstructionTarget,
  SetupInstructionTargetId,
  SetupInstructionsChange,
} from "../../../shared/setup-instructions.js";

export type InstructionTargetId = SetupInstructionTargetId;
export type InstructionTarget = SetupInstructionTarget;

export interface AgentInstructionDirs extends SetupInstructionDirs {}

export interface InstallAgentInstructionsOptions extends AgentInstructionDirs {
  guidesDir: string;
  targets?: readonly InstructionTargetId[];
}

export type AgentInstructionsChange = SetupInstructionsChange;

export interface AgentInstructionCheck {
  ok: boolean;
  message: string;
  missing: string[];
}
