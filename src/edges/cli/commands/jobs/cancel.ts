import { cancelJob } from "../../../../services/jobs/index.js";
import type { CancelJobRequest } from "../../../../services/jobs/index.js";
import {
  renderCancelJobResult,
  type JobsCommandResult,
} from "./render.js";

export interface JobCancelCommandOptions {
  cwd: string;
  jobId: string;
  json?: boolean;
  now?: () => Date;
  signalProcess: (pid: number, signal: NodeJS.Signals) => void;
}

export async function runJobsCancel(
  options: JobCancelCommandOptions,
): Promise<JobsCommandResult> {
  return renderCancelJobResult(
    await cancelJob(toCancelJobRequest(options)),
    options.json,
  );
}

function toCancelJobRequest(
  options: JobCancelCommandOptions,
): CancelJobRequest {
  return {
    cwd: options.cwd,
    jobId: options.jobId,
    now: options.now,
    signalProcess: options.signalProcess,
  };
}
