import type { OperationSpec } from "../operations/spec.js";
import { initializeJobLog } from "../stores/jobs/logs.js";
import {
  jobRecordPath,
  writeJobRecord,
} from "../stores/jobs/records.js";
import { writeJobSpec } from "../stores/jobs/specs.js";
import {
  startJobWorkerProcess,
  type SpawnBackgroundFn,
} from "./background-process.js";
import { createJobId } from "./ids.js";
import {
  buildQueuedJobRecord,
  finishJobRecord,
} from "./record-factory.js";
import type { JobRecord } from "./types.js";

export interface StartBackgroundJobOptions {
  repoRoot: string;
  spec: OperationSpec;
  jobId?: string;
  now?: () => Date;
  spawnBackground?: SpawnBackgroundFn;
  entrypoint?: string;
  workerEnvironment: NodeJS.ProcessEnv;
}

export interface StartBackgroundJobResult {
  jobId: string;
  record: JobRecord;
  childPid: number;
}

export async function startBackgroundJob(
  options: StartBackgroundJobOptions,
): Promise<StartBackgroundJobResult> {
  const now = options.now ?? (() => new Date());
  const jobId = options.jobId ?? createJobId(now());
  await writeJobSpec(options.repoRoot, jobId, options.spec);
  const recordPath = jobRecordPath(options.repoRoot, jobId);
  const queued = buildQueuedJobRecord({
    jobId,
    repoRoot: options.repoRoot,
    spec: options.spec,
    queuedAt: now(),
  });
  await writeJobRecord(recordPath, queued);
  await initializeJobLog(queued.logPath);

  const entrypoint = options.entrypoint ?? process.argv[1];
  if (entrypoint === undefined || entrypoint.length === 0) {
    const error = "cannot start background process without an entrypoint";
    await markQueuedJobFailed({ recordPath, queued, now, error });
    throw new Error(error);
  }

  let child;
  try {
    child = startJobWorkerProcess({
      repoRoot: options.repoRoot,
      entrypoint,
      environment: options.workerEnvironment,
      spawnBackground: options.spawnBackground,
    });
  } catch (err: unknown) {
    await markQueuedJobFailed({
      recordPath,
      queued,
      now,
      error: err instanceof Error ? err.message : String(err),
    });
    throw err;
  }
  child.unref?.();
  const childPid = child.pid ?? 0;
  return { jobId, record: queued, childPid };
}

async function markQueuedJobFailed(args: {
  recordPath: string;
  queued: JobRecord;
  now: () => Date;
  error: string;
}): Promise<void> {
  await writeJobRecord(
    args.recordPath,
    finishJobRecord({
      record: args.queued,
      status: "failed",
      finishedAt: args.now(),
      error: args.error,
    }),
  );
}
