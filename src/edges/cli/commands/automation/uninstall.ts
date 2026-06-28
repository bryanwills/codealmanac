import {
  uninstallAutomation,
  type AutomationScheduler,
  type AutomationTaskId,
  type AutomationUninstallOptions,
} from "../../../../services/automation/index.js";
import {
  renderAutomationUninstallResult,
  type AutomationCommandResult,
} from "./render.js";

export interface AutomationUninstallCommandOptions {
  tasks?: AutomationTaskId[];
  homeDir: string;
  plistPath?: string;
  gardenPlistPath?: string;
  updatePlistPath?: string;
  scheduler: AutomationScheduler;
}

export async function runAutomationUninstall(
  options: AutomationUninstallCommandOptions,
): Promise<AutomationCommandResult> {
  return renderAutomationUninstallResult(
    await uninstallAutomation(toAutomationUninstallOptions(options)),
  );
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
    scheduler: options.scheduler,
  };
}
