import type { AgentProviderId } from "../shared/agent-provider.js";
import type {
  AgentProviderModelChoice,
  AgentProviderReadinessStatus,
  AgentProviderStatus,
  AgentReadinessSpawnCliFn,
  AgentReadinessSpawnedProcess,
} from "../shared/agent-readiness.js";

export type SpawnedProcess = AgentReadinessSpawnedProcess;
export type SpawnCliFn = AgentReadinessSpawnCliFn;

export interface AgentProviderRuntime {
  spawnCli?: SpawnCliFn;
  environment: NodeJS.ProcessEnv;
}

export interface AgentProviderMetadata {
  id: AgentProviderId;
  displayName: string;
  defaultModel: string | null;
  executable: string;
}

export type ProviderStatus = AgentProviderStatus;
export type ProviderReadinessStatus = AgentProviderReadinessStatus;
export type ProviderModelChoice = AgentProviderModelChoice;

export interface AgentProvider {
  metadata: AgentProviderMetadata;
  checkStatus(runtime: AgentProviderRuntime): Promise<ProviderStatus>;
  assertReady(runtime: AgentProviderRuntime): Promise<void>;
  modelChoices?(opts: {
    configuredModel: string | null;
    spawnCli?: SpawnCliFn;
  }): Promise<ProviderModelChoice[]> | ProviderModelChoice[];
}
