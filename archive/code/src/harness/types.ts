import type { HarnessEvent, HarnessResult } from "./events.js";
import type { AgentProviderId } from "../agent/provider-id.js";
import type { OperationSpec } from "../operations/spec.js";

export type HarnessProviderId = AgentProviderId;

export interface HarnessCapabilities {
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
  id: HarnessProviderId;
  displayName: string;
  defaultModel: string | null;
  capabilities: HarnessCapabilities;
}

export interface ProviderStatus {
  id: HarnessProviderId;
  installed: boolean;
  authenticated: boolean;
  detail: string;
}

export interface HarnessRunHooks {
  onEvent?: (event: HarnessEvent) => void | Promise<void>;
}

export interface HarnessProvider {
  metadata: ProviderMetadata;
  checkStatus(): Promise<ProviderStatus>;
  run(spec: OperationSpec, hooks?: HarnessRunHooks): Promise<HarnessResult>;
}
