import { emit } from "./helpers.js";
import {
  parseAutomationTaskIds,
  type AutomationTaskId,
} from "../../services/automation/index.js";

export function parseAutomationTasksOrEmit(
  tasks: string[],
): AutomationTaskId[] | null {
  const parsed = parseAutomationTaskIds(tasks);
  if (parsed.ok) return parsed.tasks;

  emit({ stdout: "", stderr: `almanac: ${parsed.error}\n`, exitCode: 1 });
  return null;
}
