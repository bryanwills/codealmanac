import type { JobRecord } from "../../stores/jobs/index.js";

export type JobDisplayStatus = JobRecord["status"] | "stale";

export interface JobView extends JobRecord {
  displayStatus: JobDisplayStatus;
  elapsedMs: number;
}

export function toJobView(args: {
  record: JobRecord;
  now: Date;
  isPidAlive: (pid: number) => boolean;
}): JobView {
  const started = Date.parse(args.record.startedAt);
  const finished =
    args.record.finishedAt !== undefined
      ? Date.parse(args.record.finishedAt)
      : undefined;
  const elapsedMs =
    args.record.durationMs ??
    (Number.isFinite(started)
      ? Math.max(0, (finished ?? args.now.getTime()) - started)
      : 0);
  const displayStatus =
    args.record.status === "running" && !args.isPidAlive(args.record.pid)
      ? "stale"
      : args.record.status;
  return {
    ...args.record,
    displayStatus,
    elapsedMs,
    error:
      displayStatus === "stale"
        ? "process ended without a final status"
        : args.record.error,
  };
}
