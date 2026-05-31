import {
  AGENT_PROVIDER_IDS,
  isAgentProviderId,
  type AgentProviderId,
  type GlobalConfig,
} from "../../config/index.js";

export type ConfigKey =
  | "update_notifier"
  | "auto_commit"
  | "agent.default"
  | `agent.models.${AgentProviderId}`
  | "automation.capture_since"
  | "connectors.composio.api_key_env"
  | "connectors.github.default_account";

export interface ConfigEntry {
  key: ConfigKey;
  value: string | boolean | null;
}

export const CONFIG_KEYS: ConfigKey[] = [
  "update_notifier",
  "auto_commit",
  "agent.default",
  ...AGENT_PROVIDER_IDS.map((id) => `agent.models.${id}` as const),
  "automation.capture_since",
  "connectors.composio.api_key_env",
  "connectors.github.default_account",
];

export function parseConfigKey(raw: string): ConfigKey | null {
  if (
    raw === "update_notifier" ||
    raw === "auto_commit" ||
    raw === "agent.default" ||
    raw === "automation.capture_since" ||
    raw === "connectors.composio.api_key_env" ||
    raw === "connectors.github.default_account"
  ) return raw;
  const prefix = "agent.models.";
  if (!raw.startsWith(prefix)) return null;
  const provider = raw.slice(prefix.length);
  if (!isAgentProviderId(provider)) return null;
  return `agent.models.${provider}`;
}

export function getConfigValue(
  config: GlobalConfig,
  key: ConfigKey,
): string | boolean | null {
  if (key === "update_notifier") return config.update_notifier;
  if (key === "auto_commit") return config.auto_commit;
  if (key === "agent.default") return config.agent.default;
  if (key === "automation.capture_since") return config.automation.capture_since;
  if (key === "connectors.composio.api_key_env") {
    return config.connectors.composio.api_key_env;
  }
  if (key === "connectors.github.default_account") {
    return config.connectors.github.default_account;
  }
  const provider = providerFromModelKey(key);
  return config.agent.models[provider] ?? null;
}

export function setConfigValue(
  config: GlobalConfig,
  key: ConfigKey,
  rawValue: string | null,
): GlobalConfig {
  if (key === "update_notifier") {
    return {
      ...config,
      update_notifier: parseBoolean(rawValue),
    };
  }
  if (key === "auto_commit") {
    return {
      ...config,
      auto_commit: parseBoolean(rawValue, "auto_commit"),
    };
  }
  if (key === "agent.default") {
    if (rawValue === null || !isAgentProviderId(rawValue)) {
      throw new Error("agent.default must be one of: claude, codex, cursor");
    }
    return {
      ...config,
      agent: {
        ...config.agent,
        default: rawValue,
      },
    };
  }
  if (key === "automation.capture_since") {
    return {
      ...config,
      automation: {
        ...config.automation,
        capture_since: normalizeCaptureSince(rawValue),
      },
    };
  }
  if (key === "connectors.composio.api_key_env") {
    return {
      ...config,
      connectors: {
        ...config.connectors,
        composio: {
          ...config.connectors.composio,
          api_key_env: normalizeEnvName(rawValue),
        },
      },
    };
  }
  if (key === "connectors.github.default_account") {
    return {
      ...config,
      connectors: {
        ...config.connectors,
        github: {
          ...config.connectors.github,
          default_account: normalizeDefaultAccount(rawValue),
        },
      },
    };
  }
  const provider = providerFromModelKey(key);
  const model = normalizeModel(rawValue);
  return {
    ...config,
    agent: {
      ...config.agent,
      models: {
        ...config.agent.models,
        [provider]: model,
      },
    },
  };
}

export function configEntries(config: GlobalConfig): ConfigEntry[] {
  return CONFIG_KEYS.map((key) => ({
    key,
    value: getConfigValue(config, key),
  }));
}

export function formatConfigValue(value: string | boolean | null): string {
  if (value === null) return "default";
  return String(value);
}

function providerFromModelKey(key: ConfigKey): AgentProviderId {
  const provider = key.slice("agent.models.".length);
  if (!isAgentProviderId(provider)) {
    throw new Error(`not a model key: ${key}`);
  }
  return provider;
}

function parseBoolean(value: string | null, key = "update_notifier"): boolean {
  if (value === "true") return true;
  if (value === "false") return false;
  throw new Error(`${key} must be true or false`);
}

function normalizeModel(value: string | null): string | null {
  if (value === null) return null;
  if (value === "default" || value === "null") return null;
  if (value.length === 0) {
    throw new Error("model must be non-empty, default, or null");
  }
  return value;
}

function normalizeCaptureSince(value: string | null): string | null {
  if (value === null || value === "default" || value === "null") return null;
  if (!Number.isFinite(Date.parse(value))) {
    throw new Error("automation.capture_since must be an ISO timestamp, default, or null");
  }
  return value;
}

function normalizeEnvName(value: string | null): string {
  if (value === null || value.length === 0) {
    throw new Error("connectors.composio.api_key_env must be a non-empty environment variable name");
  }
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(value)) {
    throw new Error("connectors.composio.api_key_env must be an environment variable name");
  }
  return value;
}

function normalizeDefaultAccount(value: string | null): string | null {
  if (value === null || value === "default" || value === "null") return null;
  if (!/^[A-Za-z0-9_.-]+$/.test(value)) {
    throw new Error("connectors.github.default_account must be a connector account alias, default, or null");
  }
  return value;
}
