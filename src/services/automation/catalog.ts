import { homedir } from "node:os";

import {
  defaultSyncPlistPath,
  isScheduledTaskId,
  type ScheduledTaskId,
} from "../../platform/automation/tasks.js";

export type AutomationTaskId = ScheduledTaskId;

export function defaultSyncAutomationPlistPath(
  home: string = homedir(),
): string {
  return defaultSyncPlistPath(home);
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
