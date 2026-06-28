import type { ConfigOrigin } from "../../stores/config/index.js";
import type { ConfigKey } from "./keys.js";

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
