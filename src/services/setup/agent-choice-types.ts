export interface SetupSpawnedProcess {
  stdout: { on: (event: "data", cb: (data: Buffer | string) => void) => void };
  stderr: { on: (event: "data", cb: (data: Buffer | string) => void) => void };
  on: (event: "close" | "error", cb: (arg: number | null | Error) => void) => void;
  kill: (signal?: string) => void;
}

export type SetupSpawnCliFn = (args: string[]) => SetupSpawnedProcess;

export type SetupAgentProviderId = "claude" | "codex" | "cursor";
export type SetupProviderReadiness = "ready" | "not-authenticated" | "missing";

export interface SetupProviderModelChoice {
  value: string | null;
  label: string;
  recommended: boolean;
  source: "configured" | "provider-default" | "catalog" | "custom";
}

export interface SetupProviderChoice {
  id: SetupAgentProviderId;
  label: string;
  selected: boolean;
  recommended: boolean;
  readiness: SetupProviderReadiness;
  ready: boolean;
  installed: boolean;
  authenticated: boolean;
  effectiveModel: string | null;
  providerDefaultModel: string | null;
  configuredModel: string | null;
  account: string | null;
  detail: string;
  fixCommand: string | null;
  modelChoices: SetupProviderModelChoice[];
}

export interface SetupProviderView {
  defaultProvider: SetupAgentProviderId;
  recommendedProvider: SetupAgentProviderId;
  choices: SetupProviderChoice[];
}

export interface SetupConfiguredModels {
  claude: string | null;
  codex: string | null;
  cursor: string | null;
}

export interface SetupAgentChoiceState {
  selected: string;
  view: SetupProviderView | null;
  configuredModels: SetupConfiguredModels;
}

export type SetupAgentSelection =
  | { ok: true; provider: SetupAgentProviderId; parsedModel?: string }
  | { ok: false; error: string };
