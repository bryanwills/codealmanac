import { createAgentReadinessRuntime } from "./agent-readiness-runtime.js";
import { readDiagnosticClaudeAuth } from "./diagnostic-auth.js";
import { probeDiagnosticAutomation } from "../platform/diagnostics/automation.js";
import { probeDiagnosticInstall } from "../platform/diagnostics/install.js";
import {
  probeDiagnosticGuides,
  probeDiagnosticInstructionEntries,
} from "../platform/diagnostics/instructions.js";
import { pathsEqualOnCurrentPlatform } from "../platform/path-case.js";
import {
  readDiagnosticUpdateStatus,
  type DoctorOptions,
} from "../services/diagnostics/index.js";

export type DoctorRuntimeFacts = Pick<
  DoctorOptions,
  | "agentReadinessRuntime"
  | "authStatus"
  | "automationStatus"
  | "claudeApiKeySet"
  | "environment"
  | "guideStatus"
  | "installStatus"
  | "instructionEntriesStatus"
  | "nodeVersion"
  | "registryPathEquals"
  | "updateStatus"
>;

export async function readDoctorRuntimeFacts(options: {
  environment: NodeJS.ProcessEnv;
  homeDir: string;
  nodeVersion: string;
}): Promise<DoctorRuntimeFacts> {
  return {
    claudeApiKeySet: options.environment.ANTHROPIC_API_KEY !== undefined &&
      options.environment.ANTHROPIC_API_KEY.length > 0,
    environment: options.environment,
    nodeVersion: options.nodeVersion,
    authStatus: await readDiagnosticClaudeAuth(),
    agentReadinessRuntime: createAgentReadinessRuntime(),
    automationStatus: await probeDiagnosticAutomation(),
    guideStatus: probeDiagnosticGuides(),
    instructionEntriesStatus: await probeDiagnosticInstructionEntries(),
    updateStatus: await readDiagnosticUpdateStatus(),
    installStatus: probeDiagnosticInstall({ homeDir: options.homeDir }),
    registryPathEquals: pathsEqualOnCurrentPlatform,
  };
}
