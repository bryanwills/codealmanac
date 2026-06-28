import type { AgentProviderId } from "./agent-provider.js";

export interface AgentReadinessSpawnedProcess {
  stdout: { on: (event: "data", cb: (data: Buffer | string) => void) => void };
  stderr: { on: (event: "data", cb: (data: Buffer | string) => void) => void };
  on: (event: "close" | "error", cb: (arg: number | null | Error) => void) => void;
  kill: (signal?: string) => void;
}

export type AgentReadinessSpawnCliFn = (
  args: string[],
) => AgentReadinessSpawnedProcess;

export interface AgentProviderStatus {
  id: AgentProviderId;
  installed: boolean;
  authenticated: boolean;
  readiness: AgentProviderReadinessStatus;
  detail: string;
  accountLabel?: string;
  installFix?: string;
  loginFix?: string;
}

export type AgentProviderReadinessStatus =
  | "ready"
  | "missing_executable"
  | "not_authenticated"
  | "unknown";

export interface AgentProviderModelChoice {
  value: string | null;
  label: string;
  recommended: boolean;
  source: "configured" | "provider-default" | "catalog" | "custom";
}

export interface AgentReadinessStatusRequest {
  spawnCli?: AgentReadinessSpawnCliFn;
  environment: NodeJS.ProcessEnv;
}

export interface AgentModelChoicesRequest {
  provider: AgentProviderId;
  configuredModel: string | null;
  spawnCli?: AgentReadinessSpawnCliFn;
}

export interface AgentReadinessRuntime {
  listStatuses(
    request: AgentReadinessStatusRequest,
  ): Promise<AgentProviderStatus[]>;
  listModelChoices?(
    request: AgentModelChoicesRequest,
  ): Promise<AgentProviderModelChoice[] | null> | AgentProviderModelChoice[] | null;
}
