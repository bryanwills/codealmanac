import {
  readConfigWithOrigins,
} from "../../stores/config/index.js";
import {
  configEntries,
  getConfigValue,
  parseConfigKey,
  type ConfigKey,
} from "./keys.js";
import type {
  ConfigReadResult,
  ConfigRow,
  ConfigServiceOptions,
} from "./config-types.js";

export async function listConfigEntries(
  opts: ConfigServiceOptions,
): Promise<ConfigRow[]> {
  const { config, origins } = await readConfigWithOrigins({ cwd: opts.cwd });
  return configEntries(config).map((entry) => ({
    ...entry,
    origin: origins[entry.key] ?? "default",
  }));
}

export async function readConfigEntry(
  key: ConfigKey,
  opts: ConfigServiceOptions,
): Promise<ConfigRow> {
  const { config, origins } = await readConfigWithOrigins({ cwd: opts.cwd });
  return {
    key,
    value: getConfigValue(config, key),
    origin: origins[key] ?? "default",
  };
}

export async function readConfigEntryByKey(
  input: { key: string } & ConfigServiceOptions,
): Promise<ConfigReadResult> {
  const key = parseConfigKey(input.key);
  if (key === null) return { status: "unknown-key", key: input.key };
  return {
    status: "read",
    row: await readConfigEntry(key, input),
  };
}
