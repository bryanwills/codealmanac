import {
  AGENT_PROVIDER_IDS,
  isAgentProviderId,
  type AgentProviderId,
} from "./providers.js";

export interface AgentConfig {
  /** Default provider for agent-backed lifecycle commands. Default: "codex". */
  default: AgentProviderId;
  /** Optional per-provider model override. `null` means provider default. */
  models: Partial<Record<AgentProviderId, string | null>>;
}

export interface AutomationConfig {
  /** ISO timestamp from which scheduled capture should consider transcripts. */
  capture_since: string | null;
}

export interface ComposioConfig {
  /** Environment variable that holds the Composio project API key. */
  api_key_env: string;
  /** Stable Composio user id for this Almanac install. */
  user_id: string | null;
}

export interface GitHubConnectorAccountConfig {
  /** User-facing account alias, stored redundantly for readable config files. */
  alias: string;
  /** Composio connected account id for this GitHub account. */
  connected_account_id: string;
  /** Last observed Composio account status. */
  status: string | null;
}

export interface GitHubConnectorConfig {
  /** Default account alias for GitHub operations. */
  default_account: string | null;
  /** Connected GitHub accounts keyed by local alias. */
  accounts: Record<string, GitHubConnectorAccountConfig>;
}

export interface ConnectorsConfig {
  composio: ComposioConfig;
  github: GitHubConnectorConfig;
}

export interface GlobalConfig {
  /** When `false`, suppress the pre-command update-nag banner. Default: true. */
  update_notifier: boolean;
  /** Whether AI lifecycle runs may create git commits for wiki source files. Default: true. */
  auto_commit: boolean;
  /** Agent-provider settings for agent-backed lifecycle commands. */
  agent: AgentConfig;
  /** Scheduled auto-capture settings. */
  automation: AutomationConfig;
  /** External connector settings. Secrets live in env vars, not config files. */
  connectors: ConnectorsConfig;
}

export function defaultConfig(): GlobalConfig {
  return {
    update_notifier: true,
    auto_commit: true,
    agent: {
      default: "codex",
      models: {
        claude: null,
        codex: null,
        cursor: null,
      },
    },
    automation: {
      capture_since: null,
    },
    connectors: {
      composio: {
        api_key_env: "COMPOSIO_API_KEY",
        user_id: null,
      },
      github: {
        default_account: null,
        accounts: {},
      },
    },
  };
}

export function normalizeRawConfig(raw: Record<string, unknown>): GlobalConfig {
  const defaults = defaultConfig();
  const rawAgent =
    raw.agent !== undefined &&
    raw.agent !== null &&
    typeof raw.agent === "object" &&
    !Array.isArray(raw.agent)
      ? (raw.agent as Partial<AgentConfig>)
      : {};
  const rawDefault =
    typeof rawAgent.default === "string" &&
    isAgentProviderId(rawAgent.default)
      ? rawAgent.default
      : defaults.agent.default;
  const rawModels =
    rawAgent.models !== undefined &&
    rawAgent.models !== null &&
    typeof rawAgent.models === "object" &&
    !Array.isArray(rawAgent.models)
      ? (rawAgent.models as Record<string, unknown>)
      : {};
  const models: Partial<Record<AgentProviderId, string | null>> = {
    ...defaults.agent.models,
  };
  for (const id of AGENT_PROVIDER_IDS) {
    const value = rawModels[id];
    if (typeof value === "string" && value.length > 0) {
      models[id] = value === "default" || value === "null" ? null : value;
    } else if (value === null) {
      models[id] = null;
    }
  }
  const rawAutomation =
    raw.automation !== undefined &&
    raw.automation !== null &&
    typeof raw.automation === "object" &&
    !Array.isArray(raw.automation)
      ? raw.automation as Record<string, unknown>
      : {};
  const captureSince =
    typeof rawAutomation.capture_since === "string" &&
      Number.isFinite(Date.parse(rawAutomation.capture_since))
      ? rawAutomation.capture_since
      : defaults.automation.capture_since;
  const rawConnectors = objectRecord(raw.connectors);
  const rawComposio = objectRecord(rawConnectors.composio);
  const rawGithub = objectRecord(rawConnectors.github);
  const rawGithubAccounts = objectRecord(rawGithub.accounts);
  const accounts: Record<string, GitHubConnectorAccountConfig> = {};
  for (const [alias, value] of Object.entries(rawGithubAccounts)) {
    if (!isConnectorAlias(alias)) continue;
    const account = objectRecord(value);
    const connectedAccountId = stringValue(account.connected_account_id);
    if (connectedAccountId === null) continue;
    accounts[alias] = {
      alias: stringValue(account.alias) ?? alias,
      connected_account_id: connectedAccountId,
      status: stringValue(account.status),
    };
  }
  const defaultAccount = stringValue(rawGithub.default_account);
  return {
    update_notifier:
      typeof raw.update_notifier === "boolean"
        ? raw.update_notifier
        : defaults.update_notifier,
    auto_commit:
      typeof raw.auto_commit === "boolean"
        ? raw.auto_commit
        : defaults.auto_commit,
    agent: {
      default: rawDefault,
      models,
    },
    automation: {
      capture_since: captureSince,
    },
    connectors: {
      composio: {
        api_key_env:
          stringValue(rawComposio.api_key_env) ??
          defaults.connectors.composio.api_key_env,
        user_id: stringValue(rawComposio.user_id),
      },
      github: {
        default_account:
          defaultAccount !== null && isConnectorAlias(defaultAccount)
            ? defaultAccount
            : defaults.connectors.github.default_account,
        accounts,
      },
    },
  };
}

export function normalizeConfig(
  config: GlobalConfig | Partial<GlobalConfig>,
): GlobalConfig {
  const defaults = defaultConfig();
  return {
    update_notifier:
      typeof config.update_notifier === "boolean"
        ? config.update_notifier
        : defaults.update_notifier,
    auto_commit:
      typeof config.auto_commit === "boolean"
        ? config.auto_commit
        : defaults.auto_commit,
    agent: {
      default:
        config.agent !== undefined && isAgentProviderId(config.agent.default)
          ? config.agent.default
          : defaults.agent.default,
      models: {
        ...defaults.agent.models,
        ...(config.agent?.models ?? {}),
      },
    },
    automation: {
      capture_since: normalizeCaptureSince(
        config.automation?.capture_since,
        defaults.automation.capture_since,
      ),
    },
    connectors: normalizeConnectorsConfig(config.connectors, defaults.connectors),
  };
}

export function applyProjectConfig(
  target: Record<string, unknown>,
  projectRaw: Record<string, unknown>,
): void {
  const projectAgent =
    projectRaw.agent !== null &&
    typeof projectRaw.agent === "object" &&
    !Array.isArray(projectRaw.agent)
      ? projectRaw.agent as Record<string, unknown>
      : {};
  if (Object.keys(projectAgent).length === 0) return;
  const targetAgent =
    target.agent !== null &&
    typeof target.agent === "object" &&
    !Array.isArray(target.agent)
      ? target.agent as Record<string, unknown>
      : {};
  target.agent = targetAgent;
  if (typeof projectAgent.default === "string") {
    targetAgent.default = projectAgent.default;
  }
  const projectModels =
    projectAgent.models !== null &&
    typeof projectAgent.models === "object" &&
    !Array.isArray(projectAgent.models)
      ? projectAgent.models as Record<string, unknown>
      : {};
  if (Object.keys(projectModels).length === 0) return;
  const targetModels =
    targetAgent.models !== null &&
    typeof targetAgent.models === "object" &&
    !Array.isArray(targetAgent.models)
      ? targetAgent.models as Record<string, unknown>
      : {};
  targetAgent.models = targetModels;
  for (const id of AGENT_PROVIDER_IDS) {
    if (Object.prototype.hasOwnProperty.call(projectModels, id)) {
      targetModels[id] = projectModels[id];
    }
  }
}

export function normalizeCaptureSince(
  value: string | null | undefined,
  fallback: string | null,
): string | null {
  if (typeof value !== "string") return fallback;
  return Number.isFinite(Date.parse(value)) ? value : fallback;
}

export function isConnectorAlias(alias: string): boolean {
  return /^[A-Za-z0-9_.-]+$/.test(alias);
}

function normalizeConnectorsConfig(
  config: Partial<ConnectorsConfig> | undefined,
  defaults: ConnectorsConfig,
): ConnectorsConfig {
  const rawAccounts = config?.github?.accounts ?? {};
  const accounts: Record<string, GitHubConnectorAccountConfig> = {};
  for (const [alias, account] of Object.entries(rawAccounts)) {
    if (!isConnectorAlias(alias)) continue;
    if (typeof account.connected_account_id !== "string" ||
      account.connected_account_id.length === 0) continue;
    accounts[alias] = {
      alias: account.alias.length > 0 ? account.alias : alias,
      connected_account_id: account.connected_account_id,
      status: account.status ?? null,
    };
  }
  const requestedDefault = config?.github?.default_account ?? null;
  return {
    composio: {
      api_key_env:
        config?.composio?.api_key_env !== undefined &&
        config.composio.api_key_env.length > 0
          ? config.composio.api_key_env
          : defaults.composio.api_key_env,
      user_id: config?.composio?.user_id ?? defaults.composio.user_id,
    },
    github: {
      default_account:
        requestedDefault !== null && isConnectorAlias(requestedDefault)
          ? requestedDefault
          : defaults.github.default_account,
      accounts,
    },
  };
}

function objectRecord(value: unknown): Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? value as Record<string, unknown>
    : {};
}

function stringValue(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}
