import type { AutomationTaskId } from "./types.js";

export const SYNC_LABEL = "com.codealmanac.sync";
export const GARDEN_LABEL = "com.codealmanac.garden";
export const UPDATE_LABEL = "com.codealmanac.update";

export const DEFAULT_SYNC_INTERVAL = "5h";
export const DEFAULT_SYNC_QUIET = "45m";
export const DEFAULT_GARDEN_INTERVAL = "4h";
export const DEFAULT_UPDATE_INTERVAL = "1d";

export type AutomationTaskWorkingDirectory = "none" | "nearest-almanac-repo";

export interface AutomationTaskDefinition {
  id: AutomationTaskId;
  label: string;
  defaultInterval: string;
  stdoutLogName: string;
  stderrLogName: string;
  workingDirectory: AutomationTaskWorkingDirectory;
}

export const SYNC_TASK: AutomationTaskDefinition = {
  id: "sync",
  label: SYNC_LABEL,
  defaultInterval: DEFAULT_SYNC_INTERVAL,
  stdoutLogName: "sync.out.log",
  stderrLogName: "sync.err.log",
  workingDirectory: "none",
};

export const GARDEN_TASK: AutomationTaskDefinition = {
  id: "garden",
  label: GARDEN_LABEL,
  defaultInterval: DEFAULT_GARDEN_INTERVAL,
  stdoutLogName: "garden.out.log",
  stderrLogName: "garden.err.log",
  workingDirectory: "nearest-almanac-repo",
};

export const UPDATE_TASK: AutomationTaskDefinition = {
  id: "update",
  label: UPDATE_LABEL,
  defaultInterval: DEFAULT_UPDATE_INTERVAL,
  stdoutLogName: "update.out.log",
  stderrLogName: "update.err.log",
  workingDirectory: "none",
};

export const AUTOMATION_TASKS = {
  sync: SYNC_TASK,
  garden: GARDEN_TASK,
  update: UPDATE_TASK,
} as const;

export const DEFAULT_AUTOMATION_TASK_IDS: AutomationTaskId[] = [
  "sync",
  "garden",
];

export function automationTaskDefinition(
  id: AutomationTaskId,
): AutomationTaskDefinition {
  return AUTOMATION_TASKS[id];
}

export function isAutomationTaskId(value: string): value is AutomationTaskId {
  return value === "sync" || value === "garden" || value === "update";
}

export function syncProgramArguments(
  cliProgramArguments: string[],
  quiet: string = DEFAULT_SYNC_QUIET,
): string[] {
  return [...cliProgramArguments, "sync", "--quiet", quiet];
}

export function gardenProgramArguments(cliProgramArguments: string[]): string[] {
  return [...cliProgramArguments, "garden"];
}

export function updateProgramArguments(cliProgramArguments: string[]): string[] {
  return [...cliProgramArguments, "update"];
}
