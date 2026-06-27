import type { ExecFn as PlatformExecFn } from "../../platform/automation/launchd.js";
import type {
  ScheduledTaskId as PlatformScheduledTaskId,
} from "../../platform/automation/tasks.js";

export type AutomationExecFn = PlatformExecFn;
export type AutomationTaskId = PlatformScheduledTaskId;

export interface AutomationInstallOptions {
  tasks?: AutomationTaskId[];
  every?: string;
  quiet?: string;
  gardenEvery?: string;
  gardenOff?: boolean;
  cwd?: string;
  homeDir?: string;
  plistPath?: string;
  gardenPlistPath?: string;
  updatePlistPath?: string;
  programArguments?: string[];
  gardenProgramArguments?: string[];
  updateProgramArguments?: string[];
  env?: NodeJS.ProcessEnv;
  exec?: AutomationExecFn;
  now?: Date;
  configPath?: string;
}

export interface AutomationUninstallOptions {
  tasks?: AutomationTaskId[];
  homeDir?: string;
  plistPath?: string;
  gardenPlistPath?: string;
  updatePlistPath?: string;
  exec?: AutomationExecFn;
}

export interface AutomationStatusOptions {
  tasks?: AutomationTaskId[];
  homeDir?: string;
  plistPath?: string;
  gardenPlistPath?: string;
  updatePlistPath?: string;
  legacyCapturePlistPath?: string;
  exec?: AutomationExecFn;
}

export interface InstalledAutomationTask {
  taskId: AutomationTaskId;
  intervalInput: string;
  command: string[];
  plistPath: string;
  quiet: string | null;
}

export type AutomationInstallResult =
  | {
    status: "installed";
    tasks: InstalledAutomationTask[];
    gardenDisabled: boolean;
    syncSince: string | null;
  }
  | { status: "invalid"; error: string }
  | {
    status: "activation-failed";
    taskId: AutomationTaskId;
    plistPath: string;
    message: string;
  };

export type AutomationUninstallResult =
  | { status: "removed"; plistPaths: string[] }
  | { status: "not-installed" };

export type AutomationStatusSection =
  | {
    status: "task";
    taskId: AutomationTaskId;
    installed: boolean;
    plistPath: string;
    loaded: boolean;
    intervalSeconds: number | null;
    quiet: string | null;
  }
  | {
    status: "legacy-capture";
    plistPath: string;
  };

export interface AutomationStatusResult {
  status: "checked";
  sections: AutomationStatusSection[];
}
