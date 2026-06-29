import type {
  AgentUsage,
  HarnessFailure,
} from "../../events.js";
import type {
  FinalOutputResult,
  FinalOutputSpec,
} from "../../final-output.js";

export interface CodexRunState {
  success: boolean;
  result: string;
  outputSpec?: FinalOutputSpec;
  output?: FinalOutputResult;
  providerSessionId?: string;
  turns?: number;
  usage?: AgentUsage;
  error?: string;
  failure?: HarnessFailure;
  rootThreadId?: string;
  rootTurnId?: string;
  resultSourceThreadId?: string;
  resultSourceTurnId?: string;
  resultSourceRole?: "root" | "helper" | "unknown";
  agentParents?: Record<string, string | null>;
  agentLabels?: Record<string, string>;
  completedAgents?: Record<string, boolean>;
}

export interface JsonRpcNotification {
  method: string;
  params?: unknown;
}
