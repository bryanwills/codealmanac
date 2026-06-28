import {
  buildProviderModelChoices,
} from "../agents/provider-model-choices.js";
import {
  buildProviderSetupView,
} from "../agents/provider-setup-view.js";
import type { AgentReadinessRuntime } from "../../shared/agent-readiness.js";
import {
  readConfig,
  writeConfig,
} from "../../stores/config/index.js";
import {
  setupConfiguredModelsFromConfig,
  setupProviderViewFromReadinessView,
} from "./agent-choice-view.js";
import type {
  SetupAgentChoiceState,
  SetupAgentProviderId,
  SetupProviderModelChoice,
  SetupProviderView,
  SetupSpawnCliFn,
} from "./agent-choice-types.js";

export async function readSetupAgentChoiceState(input: {
  requested?: string;
  includeView: boolean;
  readinessRuntime: AgentReadinessRuntime;
  spawnCli?: SetupSpawnCliFn;
  environment: NodeJS.ProcessEnv;
}): Promise<SetupAgentChoiceState> {
  const config = await readConfig();
  return {
    selected: input.requested ?? config.agent.default,
    configuredModels: setupConfiguredModelsFromConfig(config.agent.models),
    view: input.includeView
      ? setupProviderViewFromReadinessView(
          await buildProviderSetupView({
            config,
            readinessRuntime: input.readinessRuntime,
            spawnCli: input.spawnCli,
            environment: input.environment,
          }),
        )
      : null,
  };
}

export async function refreshSetupAgentChoiceView(input: {
  readinessRuntime: AgentReadinessRuntime;
  spawnCli?: SetupSpawnCliFn;
  environment: NodeJS.ProcessEnv;
}): Promise<SetupProviderView> {
  const config = await readConfig();
  return setupProviderViewFromReadinessView(
    await buildProviderSetupView({
      config,
      readinessRuntime: input.readinessRuntime,
      spawnCli: input.spawnCli,
      environment: input.environment,
    }),
  );
}

export async function readSetupProviderModelChoices(input: {
  provider: SetupAgentProviderId;
  configuredModel: string | null;
  readinessRuntime: AgentReadinessRuntime;
  choice?: SetupProviderView["choices"][number];
}): Promise<SetupProviderModelChoice[]> {
  if (input.choice !== undefined) return input.choice.modelChoices;
  const choices = await buildProviderModelChoices(
    input.provider,
    input.configuredModel,
    { readinessRuntime: input.readinessRuntime },
  );
  return choices.map((choice) => ({ ...choice }));
}

export async function saveSetupAgentChoice(input: {
  provider: SetupAgentProviderId;
  model: string | null;
}): Promise<void> {
  const config = await readConfig();
  await writeConfig({
    ...config,
    agent: {
      ...config.agent,
      default: input.provider,
      models: {
        ...config.agent.models,
        [input.provider]: input.model,
      },
    },
  });
}
