import type { AgentProviderId } from "../../shared/agent-provider.js";
import type {
  AgentProviderModelChoice,
  AgentProviderStatus,
  AgentReadinessRuntime,
  AgentReadinessSpawnCliFn,
} from "../../shared/agent-readiness.js";
import type { GlobalConfig } from "../../stores/config/index.js";

export type ProviderModelChoice = AgentProviderModelChoice;
export type ProviderStatus = AgentProviderStatus;
export type ProviderSpawnCliFn = AgentReadinessSpawnCliFn;

export type ProviderReadiness = "ready" | "not-authenticated" | "missing";

export interface ProviderSetupChoice {
  id: AgentProviderId;
  label: string;
  selected: boolean;
  recommended: boolean;
  readiness: ProviderReadiness;
  ready: boolean;
  installed: boolean;
  authenticated: boolean;
  effectiveModel: string | null;
  providerDefaultModel: string | null;
  configuredModel: string | null;
  account: string | null;
  detail: string;
  fixCommand: string | null;
  modelChoices: ProviderModelChoice[];
}

export interface ProviderSetupView {
  defaultProvider: AgentProviderId;
  recommendedProvider: AgentProviderId;
  choices: ProviderSetupChoice[];
}

export interface ProviderViewOptions {
  config?: GlobalConfig;
  statuses?: ProviderStatus[];
  readinessRuntime?: AgentReadinessRuntime;
  spawnCli?: ProviderSpawnCliFn;
  environment: NodeJS.ProcessEnv;
}
