import type {
  SetupAgentProviderId,
  SetupProviderFixCommandRunner,
  SetupSpawnCliFn,
} from "../../../services/setup/index.js";
import type { AgentReadinessRuntime } from "../../../shared/agent-readiness.js";
import {
  readSetupAgentChoiceState,
  resolveSetupAgentSelection,
  saveSetupAgentChoice,
} from "../../../services/setup/index.js";
import { chooseProviderModel } from "./agent-model-choice.js";
import {
  chooseInteractiveSetupProvider,
  promptForSelectedProviderFix,
} from "./agent-provider-choice.js";
import {
  type SetupTheme,
  stepDone,
} from "./output.js";
import type { SetupInputStream } from "./types.js";

export type AgentChoice =
  | { ok: true; provider: SetupAgentProviderId; model: string | null }
  | { ok: false; error: string };

export async function chooseDefaultAgent(args: {
  input: SetupInputStream;
  out: NodeJS.WritableStream;
  theme: SetupTheme;
  interactive: boolean;
  requested?: string;
  requestedModel?: string;
  readinessRuntime: AgentReadinessRuntime;
  spawnCli?: SetupSpawnCliFn;
  runProviderFixCommand: SetupProviderFixCommandRunner;
  environment: NodeJS.ProcessEnv;
}): Promise<AgentChoice> {
  const state = await readSetupAgentChoiceState({
    requested: args.requested,
    includeView: args.interactive || args.requested !== undefined,
    readinessRuntime: args.readinessRuntime,
    spawnCli: args.spawnCli,
    environment: args.environment,
  });
  let view = state.view;
  let selected = state.selected;
  if (args.interactive && args.requested === undefined && view !== null) {
    const providerChoice = await chooseInteractiveSetupProvider({
      input: args.input,
      out: args.out,
      theme: args.theme,
      view,
      readinessRuntime: args.readinessRuntime,
      spawnCli: args.spawnCli,
      runProviderFixCommand: args.runProviderFixCommand,
      environment: args.environment,
    });
    selected = providerChoice.selected;
    view = providerChoice.view;
  }
  const selection = resolveSetupAgentSelection({
    selected,
    environment: args.environment,
  });
  if (!selection.ok) return selection;
  const provider = selection.provider;
  let selectedChoice = view?.choices.find((choice) => choice.id === provider);
  if (
    args.interactive &&
    selectedChoice !== undefined &&
    !selectedChoice.ready
  ) {
    const fixAttempt = await promptForSelectedProviderFix({
      input: args.input,
      out: args.out,
      theme: args.theme,
      provider,
      selectedChoice,
      readinessRuntime: args.readinessRuntime,
      spawnCli: args.spawnCli,
      runProviderFixCommand: args.runProviderFixCommand,
      environment: args.environment,
    });
    view = fixAttempt.view ?? view;
    selectedChoice = fixAttempt.selectedChoice;
  }
  if (selectedChoice !== undefined && !selectedChoice.ready) {
    return {
      ok: false,
      error: `${selectedChoice.label} is not ready: ${
        selectedChoice.fixCommand ?? selectedChoice.detail
      }`,
    };
  }
  const requestedModel = args.requestedModel ?? selection.parsedModel;
  const model = requestedModel ?? await chooseProviderModel({
    input: args.input,
    out: args.out,
    theme: args.theme,
    interactive: args.interactive,
    provider,
    choice: selectedChoice,
    configuredModel: state.configuredModels[provider] ?? null,
    readinessRuntime: args.readinessRuntime,
  });
  await saveSetupAgentChoice({ provider, model });
  if ((!args.interactive || args.requested !== undefined) && selectedChoice !== undefined) {
    const detail = selectedChoice?.ready === true
      ? "ready"
      : selectedChoice?.fixCommand ?? selectedChoice?.detail ?? "status unknown";
    stepDone(args.out, args.theme, `Agent readiness: ${detail}`);
  }
  return { ok: true, provider, model };
}
