import type { AgentRuntimeEvent, AgentRuntimeResult } from "./events.js";
import type { AgentProviderId } from "../provider-id.js";
import type { OperationSpec } from "../../operations/spec.js";

export type AgentRuntimeProviderId = AgentProviderId;

export interface AgentRuntimeCapabilities {
  nonInteractive: boolean;
  streaming: boolean;
  modelOverride: boolean;
  modelOptions: boolean;
  reasoningEffort: boolean;
  sessionPersistence: boolean;
  threadResume: boolean;
  interrupt: boolean;
  fileRead: boolean;
  fileWrite: boolean;
  shell: boolean;
  mcp: boolean;
  skills: boolean;
  usage: boolean;
  cost: boolean;
  contextUsage: boolean;
  structuredOutput: boolean;
  subagents: {
    supported: boolean;
    programmaticPerRun: boolean;
    enforcedToolScopes: boolean;
  };
  policy: {
    sandbox: boolean;
    strictToolAllowlist: boolean;
    commandApproval: boolean;
    toolHook: boolean;
  };
}

export interface ProviderMetadata {
  id: AgentRuntimeProviderId;
  displayName: string;
  defaultModel: string | null;
  capabilities: AgentRuntimeCapabilities;
}

export interface ProviderStatus {
  id: AgentRuntimeProviderId;
  installed: boolean;
  authenticated: boolean;
  detail: string;
}

export interface AgentRuntimeRunHooks {
  onEvent?: (event: AgentRuntimeEvent) => void | Promise<void>;
}

export interface AgentRuntimeProvider {
  metadata: ProviderMetadata;
  checkStatus(): Promise<ProviderStatus>;
  run(spec: OperationSpec, hooks?: AgentRuntimeRunHooks): Promise<AgentRuntimeResult>;
}
