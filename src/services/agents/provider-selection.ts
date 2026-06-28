import {
  isAgentProviderId,
  type AgentProviderId,
} from "../../shared/agent-provider.js";

export function parseAgentSelection(value: string): {
  provider: AgentProviderId | null;
  model?: string;
} {
  const [rawProvider, ...modelParts] = value.split("/");
  if (rawProvider === undefined || !isAgentProviderId(rawProvider)) {
    return { provider: null };
  }
  const model = modelParts.join("/");
  return {
    provider: rawProvider,
    model: model.length > 0 ? model : undefined,
  };
}
