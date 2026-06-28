import {
  readAutomationStatus,
  type AutomationScheduler,
  type AutomationStatusOptions,
  type AutomationTaskId,
} from "../../../../services/automation/index.js";
import {
  renderAutomationStatusResult,
  type AutomationCommandResult,
} from "./render.js";

export interface AutomationStatusCommandOptions {
  tasks?: AutomationTaskId[];
  homeDir: string;
  plistPath?: string;
  gardenPlistPath?: string;
  updatePlistPath?: string;
  legacyCapturePlistPath?: string;
  scheduler: AutomationScheduler;
}

export async function runAutomationStatus(
  options: AutomationStatusCommandOptions,
): Promise<AutomationCommandResult> {
  return renderAutomationStatusResult(
    await readAutomationStatus(toAutomationStatusOptions(options)),
  );
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
    scheduler: options.scheduler,
  };
}
