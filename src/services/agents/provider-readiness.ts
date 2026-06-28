import type { AgentProviderId } from "../../shared/agent-provider.js";
import type {
  ProviderReadiness,
  ProviderStatus,
} from "./provider-types.js";

export function providerReadiness(status: ProviderStatus): ProviderReadiness {
  if (status.readiness === "ready") return "ready";
  if (status.readiness === "not_authenticated") return "not-authenticated";
  return "missing";
}

export function providerFixCommand(status: ProviderStatus): string | null {
  if (status.readiness === "ready") return null;
  if (status.readiness === "missing_executable" || status.readiness === "unknown") {
    return status.installFix ?? null;
  }
  return status.loginFix ?? null;
}

export function missingProviderStatus(id: AgentProviderId): ProviderStatus {
  return {
    id,
    installed: false,
    authenticated: false,
    readiness: "unknown",
    detail: "provider status unavailable",
  };
}
