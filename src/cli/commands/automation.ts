import type { CommandResult } from "../helpers.js";
import {
  defaultSyncAutomationPlistPath,
  installAutomation,
  readAutomationStatus,
  uninstallAutomation,
  type AutomationTaskId,
  type AutomationInstallOptions,
  type InstalledAutomationTask,
  type AutomationStatusOptions,
  type AutomationStatusSection,
  type AutomationUninstallOptions,
} from "../../services/automation/index.js";

export type AutomationCommandExecFn = (
  file: string,
  args: string[],
) => Promise<{ stdout?: string; stderr?: string }>;

export interface AutomationInstallCommandOptions {
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
  exec?: AutomationCommandExecFn;
  now?: Date;
  configPath?: string;
}

export interface AutomationUninstallCommandOptions {
  tasks?: AutomationTaskId[];
  homeDir?: string;
  plistPath?: string;
  gardenPlistPath?: string;
  updatePlistPath?: string;
  exec?: AutomationCommandExecFn;
}

export interface AutomationStatusCommandOptions {
  tasks?: AutomationTaskId[];
  homeDir?: string;
  plistPath?: string;
  gardenPlistPath?: string;
  updatePlistPath?: string;
  legacyCapturePlistPath?: string;
  exec?: AutomationCommandExecFn;
}

const TASK_LABELS: Record<AutomationTaskId, string> = {
  sync: "sync automation",
  garden: "garden automation",
  update: "auto-update automation",
};

export async function runAutomationInstall(
  options: AutomationInstallCommandOptions = {},
): Promise<CommandResult> {
  const result = await installAutomation(toAutomationInstallOptions(options));
  if (result.status === "invalid") {
    return { stdout: "", stderr: `almanac: ${result.error}\n`, exitCode: 1 };
  }
  if (result.status === "activation-failed") {
    return {
      stdout: "",
      stderr:
        `almanac: ${TASK_LABELS[result.taskId]} plist written to ${result.plistPath}, but launchctl bootstrap failed: ${result.message}\n`,
      exitCode: 1,
    };
  }
  return {
    stdout: formatAutomationInstall({
      tasks: result.tasks,
      gardenDisabled: result.gardenDisabled,
      syncSince: result.syncSince,
    }),
    stderr: "",
    exitCode: 0,
  };
}

export async function runAutomationUninstall(
  options: AutomationUninstallCommandOptions = {},
): Promise<CommandResult> {
  const result = await uninstallAutomation(toAutomationUninstallOptions(options));
  if (result.status === "not-installed") {
    return {
      stdout: "almanac: automation not installed\n",
      stderr: "",
      exitCode: 0,
    };
  }
  return {
    stdout:
      `almanac: automation removed\n` +
      result.plistPaths.map((pathValue) => `  plist: ${pathValue}\n`).join(""),
    stderr: "",
    exitCode: 0,
  };
}

export async function runAutomationStatus(
  options: AutomationStatusCommandOptions = {},
): Promise<CommandResult> {
  const result = await readAutomationStatus(toAutomationStatusOptions(options));
  return {
    stdout: result.sections.map(formatAutomationStatusSection).join(""),
    stderr: "",
    exitCode: 0,
  };
}

export function defaultPlistPath(home?: string): string {
  return defaultSyncAutomationPlistPath(home);
}

function toAutomationInstallOptions(
  options: AutomationInstallCommandOptions,
): AutomationInstallOptions {
  return {
    tasks: options.tasks,
    every: options.every,
    quiet: options.quiet,
    gardenEvery: options.gardenEvery,
    gardenOff: options.gardenOff,
    cwd: options.cwd,
    homeDir: options.homeDir,
    plistPath: options.plistPath,
    gardenPlistPath: options.gardenPlistPath,
    updatePlistPath: options.updatePlistPath,
    programArguments: options.programArguments,
    gardenProgramArguments: options.gardenProgramArguments,
    updateProgramArguments: options.updateProgramArguments,
    env: options.env,
    exec: options.exec,
    now: options.now,
    configPath: options.configPath,
  };
}

function toAutomationUninstallOptions(
  options: AutomationUninstallCommandOptions,
): AutomationUninstallOptions {
  return {
    tasks: options.tasks,
    homeDir: options.homeDir,
    plistPath: options.plistPath,
    gardenPlistPath: options.gardenPlistPath,
    updatePlistPath: options.updatePlistPath,
    exec: options.exec,
  };
}

function toAutomationStatusOptions(
  options: AutomationStatusCommandOptions,
): AutomationStatusOptions {
  return {
    tasks: options.tasks,
    homeDir: options.homeDir,
    plistPath: options.plistPath,
    gardenPlistPath: options.gardenPlistPath,
    updatePlistPath: options.updatePlistPath,
    legacyCapturePlistPath: options.legacyCapturePlistPath,
    exec: options.exec,
  };
}

function formatAutomationInstall(result: {
  tasks: InstalledAutomationTask[];
  gardenDisabled: boolean;
  syncSince: string | null;
}): string {
  const lines = ["almanac: automation installed"];
  for (const task of result.tasks) {
    lines.push(`  ${task.taskId} interval: ${task.intervalInput}`);
    if (task.taskId === "sync") {
      if (task.quiet !== null) lines.push(`  sync quiet: ${task.quiet}`);
      if (result.syncSince !== null) {
        lines.push(`  syncing transcripts after: ${result.syncSince}`);
      }
    }
    lines.push(`  ${task.taskId} command: ${task.command.join(" ")}`);
    lines.push(`  ${task.taskId} plist: ${task.plistPath}`);
  }
  if (result.gardenDisabled) {
    lines.push("  garden: disabled");
  }
  return `${lines.join("\n")}\n`;
}

function formatAutomationStatusSection(section: AutomationStatusSection): string {
  if (section.status === "legacy-capture") {
    return formatLegacyCaptureSweepStatus(section.plistPath);
  }
  if (!section.installed) {
    return `${TASK_LABELS[section.taskId]}: not installed\n`;
  }
  const extra = section.quiet !== null ? `  quiet: ${section.quiet}\n` : "";
  return (
    `${TASK_LABELS[section.taskId]}: installed\n` +
    `  plist: ${section.plistPath}\n` +
    `  launchd loaded: ${section.loaded ? "yes" : "no"}\n` +
    (section.intervalSeconds !== null ? `  interval: ${section.intervalSeconds}s\n` : "") +
    extra
  );
}

function formatLegacyCaptureSweepStatus(plistPath: string): string {
  return (
    "legacy automation: uses removed command capture sweep\n" +
    `  plist: ${plistPath}\n` +
    "  run: almanac migrate automation\n"
  );
}
