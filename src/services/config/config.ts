import {
  deleteNestedConfigValue,
  getConfigPath,
  getProjectConfigPath,
  readConfigObject,
  readConfig,
  readConfigWithOrigins,
  setNestedConfigValue,
  type ConfigOrigin,
  writeConfigObject,
} from "../../stores/config/index.js";
import {
  configEntries,
  getConfigValue,
  isUserLevelOnlyKey,
  parseConfigKey,
  setConfigValue,
  type ConfigKey,
} from "./keys.js";

export interface ConfigServiceOptions {
  cwd: string;
}

export interface ConfigRow {
  key: ConfigKey;
  value: string | boolean | null;
  origin: ConfigOrigin;
}

export type ConfigSetResult =
  | {
      status: "set";
      key: ConfigKey;
      value: string | boolean | null;
      project: boolean;
    }
  | ConfigRejectedMutation
  | ConfigInvalidRequest;

export type ConfigUnsetResult =
  | {
      status: "unset";
      key: ConfigKey;
      project: boolean;
    }
  | ConfigRejectedMutation
  | ConfigInvalidRequest;

export type ConfigReadResult =
  | {
      status: "read";
      row: ConfigRow;
    }
  | ConfigUnknownKey;

export type ConfigInvalidRequest = ConfigUnknownKey | {
  status: "missing-value";
  key: ConfigKey;
};

export interface ConfigUnknownKey {
  status: "unknown-key";
  key: string;
}

export type ConfigRejectedMutation =
  | {
      status: "user-level-only";
      key: ConfigKey;
    }
  | {
      status: "missing-project-config";
    };

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

export async function setConfigEntryByKey(
  input: {
    key: string;
    value?: string;
    project: boolean;
  } & ConfigServiceOptions,
): Promise<ConfigSetResult> {
  const key = parseConfigKey(input.key);
  if (key === null) return { status: "unknown-key", key: input.key };
  if (input.value === undefined) return { status: "missing-value", key };
  return setConfigEntry({
    key,
    value: input.value,
    project: input.project,
    cwd: input.cwd,
  });
}

export async function setConfigEntry(
  input: {
    key: ConfigKey;
    value: string;
    project: boolean;
  } & ConfigServiceOptions,
): Promise<ConfigSetResult> {
  if (input.project && isUserLevelOnlyKey(input.key)) {
    return { status: "user-level-only", key: input.key };
  }
  const file = targetConfigPath(input.project, input.cwd);
  if (file === null) {
    return { status: "missing-project-config" };
  }

  const next = setConfigValue(
    await readConfig({ cwd: input.cwd }),
    input.key,
    input.value,
  );
  const raw = await readConfigObject(file);
  const value = getConfigValue(next, input.key);
  setNestedConfigValue(raw, configKeyPath(input.key), value);
  await writeConfigObject(raw, file);
  return {
    status: "set",
    key: input.key,
    value,
    project: input.project,
  };
}

export async function unsetConfigEntryByKey(
  input: {
    key: string;
    project: boolean;
  } & ConfigServiceOptions,
): Promise<ConfigUnsetResult> {
  const key = parseConfigKey(input.key);
  if (key === null) return { status: "unknown-key", key: input.key };
  return unsetConfigEntry({
    key,
    project: input.project,
    cwd: input.cwd,
  });
}

export async function unsetConfigEntry(
  input: {
    key: ConfigKey;
    project: boolean;
  } & ConfigServiceOptions,
): Promise<ConfigUnsetResult> {
  if (input.project && isUserLevelOnlyKey(input.key)) {
    return { status: "user-level-only", key: input.key };
  }
  const file = targetConfigPath(input.project, input.cwd);
  if (file === null) {
    return { status: "missing-project-config" };
  }

  const raw = await readConfigObject(file);
  deleteNestedConfigValue(raw, configKeyPath(input.key));
  await writeConfigObject(raw, file);
  return {
    status: "unset",
    key: input.key,
    project: input.project,
  };
}

function targetConfigPath(project: boolean, cwd: string): string | null {
  return project ? getProjectConfigPath(cwd) : getConfigPath();
}

function configKeyPath(key: ConfigKey): string[] {
  return key.split(".");
}
