import { getEnabledAgentProviderIds } from "../../shared/agent-provider-enablement.js";
import { readConfig } from "../../stores/config/index.js";
import { getProviderDefaultModel, getProviderLabel } from "./provider-catalog.js";
import { buildProviderModelChoices } from "./provider-model-choices.js";
import { chooseRecommendedProvider } from "./provider-recommendation.js";
import {
  missingProviderStatus,
  providerFixCommand,
  providerReadiness,
} from "./provider-readiness.js";
import type {
  ProviderSetupChoice,
  ProviderSetupView,
  ProviderStatus,
  ProviderViewOptions,
} from "./provider-types.js";

export async function buildProviderSetupView(
  opts: ProviderViewOptions,
): Promise<ProviderSetupView> {
  const config = opts.config ?? await readConfig();
  const statuses = opts.statuses ?? await listStatusesFromRuntime(opts);
  const statusById = new Map(statuses.map((status) => [status.id, status]));
  const recommendedProvider = chooseRecommendedProvider(
    statuses,
    opts.environment,
  );
  const choices: ProviderSetupChoice[] = [];
  for (const id of getEnabledAgentProviderIds(opts.environment)) {
    const status = statusById.get(id) ?? missingProviderStatus(id);
    const readiness = providerReadiness(status);
    const configuredModel = normalizeModel(config.agent.models[id]);
    const providerDefaultModel = getProviderDefaultModel(id);
    const effectiveModel = configuredModel ?? providerDefaultModel;
    choices.push({
      id,
      label: getProviderLabel(id),
      selected: id === config.agent.default,
      recommended: id === recommendedProvider,
      readiness,
      ready: readiness === "ready",
      installed: status.installed,
      authenticated: status.authenticated,
      effectiveModel,
      providerDefaultModel,
      configuredModel,
      account: status.authenticated ? status.accountLabel ?? null : null,
      detail: status.detail,
      fixCommand: providerFixCommand(status),
      modelChoices: await buildProviderModelChoices(id, configuredModel, {
        spawnCli: opts.spawnCli,
        readinessRuntime: opts.readinessRuntime,
      }),
    });
  }
  return {
    defaultProvider: config.agent.default,
    recommendedProvider,
    choices,
  };
}

async function listStatusesFromRuntime(
  opts: ProviderViewOptions,
): Promise<ProviderStatus[]> {
  if (opts.readinessRuntime === undefined) {
    throw new Error("provider readiness runtime is required");
  }
  return opts.readinessRuntime.listStatuses({
    spawnCli: opts.spawnCli,
    environment: opts.environment,
  });
}

function normalizeModel(value: string | null | undefined): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}
