import type { AgentRuntimeProvider, AgentRuntimeProviderId } from "../types.js";
import { createClaudeAgentRuntimeProvider } from "./claude.js";
import { createCodexAgentRuntimeProvider } from "./codex.js";
import { cursorAgentRuntimeProvider } from "./cursor.js";
import { AGENT_RUNTIME_PROVIDER_METADATA } from "./metadata.js";

export interface AgentRuntimeProviderRegistry {
  getProvider(id: AgentRuntimeProviderId): AgentRuntimeProvider;
  listProviders(): AgentRuntimeProvider[];
}

export interface AgentRuntimeProviderRegistryRuntime {
  environment: NodeJS.ProcessEnv;
}

export function createAgentRuntimeProviderRegistry(
  runtime: AgentRuntimeProviderRegistryRuntime,
): AgentRuntimeProviderRegistry {
  const providers = {
    claude: createClaudeAgentRuntimeProvider({ environment: runtime.environment }),
    codex: createCodexAgentRuntimeProvider({ environment: runtime.environment }),
    cursor: cursorAgentRuntimeProvider,
  } satisfies Record<AgentRuntimeProviderId, AgentRuntimeProvider>;

  return {
    getProvider: (id) => providers[id],
    listProviders: () => Object.values(providers),
  };
}

export { AGENT_RUNTIME_PROVIDER_METADATA };
