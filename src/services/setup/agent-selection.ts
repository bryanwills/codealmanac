import {
  disabledAgentProviderMessage,
  formatEnabledAgentProviderList,
  isEnabledAgentProviderId,
} from "../../shared/agent-provider-enablement.js";
import { parseAgentSelection } from "../agents/provider-selection.js";
import type { SetupAgentSelection } from "./agent-choice-types.js";

export function resolveSetupAgentSelection(
  input: {
    selected: string;
    environment: NodeJS.ProcessEnv;
  },
): SetupAgentSelection {
  const parsed = parseAgentSelection(input.selected);
  if (parsed.provider === null) {
    return {
      ok: false,
      error:
        `unknown agent '${input.selected}'. Expected one of: ${
          formatEnabledAgentProviderList(input.environment)
        }.`,
    };
  }
  if (!isEnabledAgentProviderId(parsed.provider, input.environment)) {
    return {
      ok: false,
      error: disabledAgentProviderMessage(parsed.provider),
    };
  }
  return {
    ok: true,
    provider: parsed.provider,
    parsedModel: parsed.model,
  };
}
