import type { HarnessEvent } from "../harness/events.js";
import {
  buildJobLogEntry,
  type AppendJobEventOptions,
  type JobLogEntry,
} from "./log-entry.js";
import {
  appendJobLogEntry,
  initializeJobLog,
} from "../stores/jobs/logs.js";

export type { AppendJobEventOptions, JobLogEntry };
export { initializeJobLog };

export async function appendJobEvent(
  path: string,
  event: HarnessEvent,
  now: Date = new Date(),
  options: AppendJobEventOptions = {},
): Promise<void> {
  await appendJobLogEntry(path, buildJobLogEntry(event, now, options));
}
