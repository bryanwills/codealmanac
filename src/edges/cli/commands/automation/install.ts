import {
  installAutomation,
  type AutomationInstallOptions,
  type AutomationScheduler,
  type AutomationTaskId,
} from "../../../../services/automation/index.js";
import {
  renderAutomationInstallResult,
  type AutomationCommandResult,
} from "./render.js";

export interface AutomationInstallCommandOptions {
  tasks?: AutomationTaskId[];
  every?: string;
  quiet?: string;
  gardenEvery?: string;
  gardenOff?: boolean;
  cwd: string;
  homeDir: string;
  pathEnvironment: string | undefined;
  cliProgramArguments: string[];
  plistPath?: string;
  gardenPlistPath?: string;
  updatePlistPath?: string;
  programArguments?: string[];
  gardenProgramArguments?: string[];
  updateProgramArguments?: string[];
  scheduler: AutomationScheduler;
  now?: Date;
  configPath?: string;
}

export async function runAutomationInstall(
  options: AutomationInstallCommandOptions,
): Promise<AutomationCommandResult> {
  return renderAutomationInstallResult(
    await installAutomation(toAutomationInstallOptions(options)),
  );
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
    pathEnvironment: options.pathEnvironment,
    cliProgramArguments: options.cliProgramArguments,
    homeDir: options.homeDir,
    plistPath: options.plistPath,
    gardenPlistPath: options.gardenPlistPath,
    updatePlistPath: options.updatePlistPath,
    programArguments: options.programArguments,
    gardenProgramArguments: options.gardenProgramArguments,
    updateProgramArguments: options.updateProgramArguments,
    scheduler: options.scheduler,
    now: options.now,
    configPath: options.configPath,
  };
}
