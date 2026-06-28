import type { AgentProviderId } from "../../shared/agent-provider.js";
import type {
  ProviderModelChoice,
  ProviderSpawnCliFn,
} from "./provider-types.js";
import type { AgentReadinessRuntime } from "../../shared/agent-readiness.js";
import { getProviderDefaultModel } from "./provider-catalog.js";

export function buildProviderModelChoices(
  id: AgentProviderId,
  configuredModel: string | null = null,
  opts: {
    readinessRuntime?: AgentReadinessRuntime;
    spawnCli?: ProviderSpawnCliFn;
  } = {},
): Promise<ProviderModelChoice[]> | ProviderModelChoice[] {
  const runtimeChoices = opts.readinessRuntime?.listModelChoices?.({
    provider: id,
    configuredModel,
    spawnCli: opts.spawnCli,
  });
  if (runtimeChoices !== undefined) {
    return resolveRuntimeModelChoices(runtimeChoices, () =>
      buildDefaultProviderModelChoices(id, configuredModel)
    );
  }
  return buildDefaultProviderModelChoices(id, configuredModel);
}

function buildDefaultProviderModelChoices(
  id: AgentProviderId,
  configuredModel: string | null,
): ProviderModelChoice[] {
  const choices: ProviderModelChoice[] = [];
  if (configuredModel !== null) {
    choices.push({
      value: configuredModel,
      label: configuredModel,
      recommended: false,
      source: "configured",
    });
  }

  const providerDefault = getProviderDefaultModel(id);
  if (providerDefault !== null) {
    if (!choices.some((choice) => choice.value === providerDefault)) {
      choices.push({
        value: providerDefault,
        label: providerDefault,
        recommended: true,
        source: "provider-default",
      });
    } else {
      choices[0] = { ...choices[0]!, recommended: true };
    }
  } else {
    choices.push({
      value: null,
      label: "provider default",
      recommended: true,
      source: "provider-default",
    });
  }

  choices.push({
    value: "__custom__",
    label: "Enter a model name",
    recommended: false,
    source: "custom",
  });
  return choices;
}

async function resolveRuntimeModelChoices(
  choices:
    | Promise<ProviderModelChoice[] | null>
    | ProviderModelChoice[]
    | null,
  fallback: () => ProviderModelChoice[],
): Promise<ProviderModelChoice[]> {
  const resolved = await choices;
  return resolved ?? fallback();
}
