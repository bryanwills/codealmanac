import {
  isScheduledTaskId,
} from "../../platform/automation/tasks.js";
import type { AutomationTaskId } from "./types.js";

const TASK_LABELS: Record<AutomationTaskId, string> = {
  sync: "sync automation",
  garden: "garden automation",
  update: "auto-update automation",
};

export function automationTaskLabel(taskId: AutomationTaskId): string {
  return TASK_LABELS[taskId];
}

export function parseAutomationTaskIds(
  values: string[],
): { ok: true; tasks: AutomationTaskId[] } | { ok: false; error: string } {
  const tasks: AutomationTaskId[] = [];
  for (const value of values) {
    if (!isScheduledTaskId(value)) {
      return {
        ok: false,
        error: `unknown automation task '${value}' (expected sync, garden, or update)`,
      };
    }
    if (!tasks.includes(value)) tasks.push(value);
  }
  return { ok: true, tasks };
}
