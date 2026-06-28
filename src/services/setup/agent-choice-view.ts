import type {
  ProviderSetupChoice,
  ProviderSetupView,
} from "../agents/provider-types.js";
import type {
  SetupAgentProviderId,
  SetupConfiguredModels,
  SetupProviderChoice,
  SetupProviderView,
} from "./agent-choice-types.js";

export function setupProviderViewFromReadinessView(
  view: ProviderSetupView,
): SetupProviderView {
  return {
    defaultProvider: view.defaultProvider,
    recommendedProvider: view.recommendedProvider,
    choices: view.choices.map(setupProviderChoiceFromReadinessChoice),
  };
}

export function setupConfiguredModelsFromConfig(
  models: Partial<Record<SetupAgentProviderId, string | null>>,
): SetupConfiguredModels {
  return {
    claude: models.claude ?? null,
    codex: models.codex ?? null,
    cursor: models.cursor ?? null,
  };
}

function setupProviderChoiceFromReadinessChoice(
  choice: ProviderSetupChoice,
): SetupProviderChoice {
  return {
    id: choice.id,
    label: choice.label,
    selected: choice.selected,
    recommended: choice.recommended,
    readiness: choice.readiness,
    ready: choice.ready,
    installed: choice.installed,
    authenticated: choice.authenticated,
    effectiveModel: choice.effectiveModel,
    providerDefaultModel: choice.providerDefaultModel,
    configuredModel: choice.configuredModel,
    account: choice.account,
    detail: choice.detail,
    fixCommand: choice.fixCommand,
    modelChoices: choice.modelChoices.map((modelChoice) => ({ ...modelChoice })),
  };
}
