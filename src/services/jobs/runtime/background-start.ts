import type { OperationSpec } from "../../lifecycle/operations/spec.js";
import { initializeJobLog } from "../../../stores/jobs/index.js";
import {
  jobRecordPath,
  writeJobRecord,
  writeJobSpec,
} from "../../../stores/jobs/index.js";
import {
  startJobWorkerProcess,
  type JobWorkerProgram,
  type SpawnBackgroundFn,
} from "../../../platform/jobs/worker-process.js";
import { createJobId } from "./ids.js";
import {
  buildQueuedJobRecord,
  finishJobRecord,
} from "../record-lifecycle.js";
import type { JobRecord } from "../../../stores/jobs/index.js";

export interface StartBackgroundJobOptions {
  repoRoot: string;
  spec: OperationSpec;
  jobId?: string;
  now?: () => Date;
  spawnBackground?: SpawnBackgroundFn;
  workerProgram: JobWorkerProgram;
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

  if (options.workerProgram.entrypoint.length === 0) {
    const error = "cannot start background process without an entrypoint";
    await markQueuedJobFailed({ recordPath, queued, now, error });
    throw new Error(error);
  }

  let child;
  try {
    child = startJobWorkerProcess({
      repoRoot: options.repoRoot,
      workerProgram: options.workerProgram,
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
