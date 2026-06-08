import { existsSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const SYNC_LABEL = "com.codealmanac.sync";
export const LEGACY_CAPTURE_SWEEP_LABEL = "com.codealmanac.capture-sweep";
export const GARDEN_LABEL = "com.codealmanac.garden";
export const UPDATE_LABEL = "com.codealmanac.update";

export const DEFAULT_SYNC_INTERVAL = "5h";
export const DEFAULT_SYNC_QUIET = "45m";
export const DEFAULT_GARDEN_INTERVAL = "4h";
export const DEFAULT_UPDATE_INTERVAL = "1d";

export type ScheduledTaskId = "sync" | "garden" | "update";
export type ScheduledTaskWorkingDirectory = "none" | "nearest-almanac-repo";

export interface ScheduledTaskDefinition {
  id: ScheduledTaskId;
  label: string;
  defaultInterval: string;
  plistPath: (home: string) => string;
  stdoutLogName: string;
  stderrLogName: string;
  workingDirectory: ScheduledTaskWorkingDirectory;
  programArguments: (options?: { quiet?: string }) => string[];
}

export const SYNC_TASK: ScheduledTaskDefinition = {
  id: "sync",
  label: SYNC_LABEL,
  defaultInterval: DEFAULT_SYNC_INTERVAL,
  plistPath: (home) =>
    path.join(home, "Library", "LaunchAgents", `${SYNC_LABEL}.plist`),
  stdoutLogName: "sync.out.log",
  stderrLogName: "sync.err.log",
  workingDirectory: "none",
  programArguments: (options) => [
    ...defaultCliProgramArguments(),
    "sync",
    "--quiet",
    options?.quiet ?? DEFAULT_SYNC_QUIET,
  ],
};

export const GARDEN_TASK: ScheduledTaskDefinition = {
  id: "garden",
  label: GARDEN_LABEL,
  defaultInterval: DEFAULT_GARDEN_INTERVAL,
  plistPath: (home) =>
    path.join(home, "Library", "LaunchAgents", `${GARDEN_LABEL}.plist`),
  stdoutLogName: "garden.out.log",
  stderrLogName: "garden.err.log",
  workingDirectory: "nearest-almanac-repo",
  programArguments: () => [...defaultCliProgramArguments(), "garden"],
};

export const UPDATE_TASK: ScheduledTaskDefinition = {
  id: "update",
  label: UPDATE_LABEL,
  defaultInterval: DEFAULT_UPDATE_INTERVAL,
  plistPath: (home) =>
    path.join(home, "Library", "LaunchAgents", `${UPDATE_LABEL}.plist`),
  stdoutLogName: "update.out.log",
  stderrLogName: "update.err.log",
  workingDirectory: "none",
  programArguments: () => [...defaultCliProgramArguments(), "update"],
};

export const SCHEDULED_TASKS = {
  sync: SYNC_TASK,
  garden: GARDEN_TASK,
  update: UPDATE_TASK,
} as const;

export const DEFAULT_AUTOMATION_TASK_IDS: ScheduledTaskId[] = ["sync", "garden"];

export function scheduledTaskDefinition(
  id: ScheduledTaskId,
): ScheduledTaskDefinition {
  return SCHEDULED_TASKS[id];
}

export function isScheduledTaskId(value: string): value is ScheduledTaskId {
  return value === "sync" || value === "garden" || value === "update";
}

export function scheduledTaskLogPaths(
  task: ScheduledTaskDefinition,
  home: string,
): { stdoutPath: string; stderrPath: string } {
  const logsDir = path.join(home, ".almanac", "logs");
  return {
    stdoutPath: path.join(logsDir, task.stdoutLogName),
    stderrPath: path.join(logsDir, task.stderrLogName),
  };
}

export function syncProgramArguments(
  quiet: string = DEFAULT_SYNC_QUIET,
): string[] {
  return SYNC_TASK.programArguments({ quiet });
}

export function gardenProgramArguments(): string[] {
  return GARDEN_TASK.programArguments();
}

export function defaultCliProgramArguments(): string[] {
  const cliEntry = findPackageCliEntry() ??
    (process.argv[1] !== undefined
      ? path.resolve(process.argv[1])
      : path.resolve(process.cwd(), "dist", "launcher.js"));
  return [process.execPath, cliEntry];
}

export function defaultCapturePlistPath(home: string = homedir()): string {
  return path.join(home, "Library", "LaunchAgents", `${LEGACY_CAPTURE_SWEEP_LABEL}.plist`);
}

export function defaultSyncPlistPath(home: string = homedir()): string {
  return SYNC_TASK.plistPath(home);
}

export function defaultGardenPlistPath(home: string = homedir()): string {
  return GARDEN_TASK.plistPath(home);
}

export function defaultUpdatePlistPath(home: string = homedir()): string {
  return UPDATE_TASK.plistPath(home);
}

function findPackageCliEntry(): string | null {
  let dir = path.dirname(fileURLToPath(import.meta.url));
  for (let i = 0; i < 8; i++) {
    const pkg = path.join(dir, "package.json");
    if (existsSync(pkg)) return path.join(dir, "dist", "launcher.js");
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}
