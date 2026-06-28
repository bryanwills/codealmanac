import {
  getEnabledAgentProviderIds,
  type AgentProviderId,
} from "../../shared/agent-provider-enablement.js";
import { providerReadiness } from "./provider-readiness.js";
import type { ProviderStatus } from "./provider-types.js";

export function chooseRecommendedProvider(
  statuses: ProviderStatus[],
  environment: NodeJS.ProcessEnv,
): AgentProviderId {
  const codexStatus = statuses.find((status) => status.id === "codex");
  if (
    codexStatus !== undefined &&
    (
      codexStatus.readiness === "ready" ||
      codexStatus.readiness === "not_authenticated"
    )
  ) {
    return "codex";
  }

  const ready = statuses
    .filter((status) => providerReadiness(status) === "ready")
    .map((status) => status.id);
  for (const id of getEnabledAgentProviderIds(environment)) {
    if (ready.includes(id)) return id;
  }
  return "codex";
}
