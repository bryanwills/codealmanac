import {
  getAgentProvider,
  listProviderStatuses,
} from "../agent/readiness/providers/index.js";
import type { AgentReadinessRuntime } from "../shared/agent-readiness.js";

export function createAgentReadinessRuntime(): AgentReadinessRuntime {
  return {
    listStatuses: listProviderStatuses,
    listModelChoices: async (request) => {
      const provider = getAgentProvider(request.provider);
      if (provider.modelChoices === undefined) return null;
      return provider.modelChoices({
        configuredModel: request.configuredModel,
        spawnCli: request.spawnCli,
      });
    },
  };
}
