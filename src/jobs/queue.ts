import { listJobRecords } from "../stores/jobs/records.js";
import type { JobRecord } from "./types.js";

export async function oldestQueuedJob(repoRoot: string): Promise<JobRecord | null> {
  const records = await listJobRecords(repoRoot);
  const queued = records.filter((record) => record.status === "queued");
  queued.sort((a, b) => a.startedAt.localeCompare(b.startedAt));
  return queued[0] ?? null;
}
