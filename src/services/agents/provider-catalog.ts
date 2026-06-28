import type { AgentProviderId } from "../../shared/agent-provider.js";
import { PROVIDER_DEFINITIONS } from "../../shared/agent-provider.js";

export function getProviderLabel(id: AgentProviderId): string {
  return PROVIDER_DEFINITIONS[id].displayName;
}

export function getProviderDefaultModel(id: AgentProviderId): string | null {
  return PROVIDER_DEFINITIONS[id].defaultModel;
}
