import {
  readJobLog,
  streamJobLog,
} from "../../../../services/jobs/index.js";
import type {
  JobLogRequest,
  StreamJobLogRequest,
} from "../../../../services/jobs/index.js";
import {
  renderJobLog,
  renderStreamJobLogResult,
  type JobsCommandResult,
} from "./render.js";

export interface JobLogCommandOptions {
  cwd: string;
  jobId: string;
  json?: boolean;
}

export interface JobAttachStreamCommandOptions {
  cwd: string;
  jobId: string;
  json?: boolean;
  now?: () => Date;
  isPidAlive: (pid: number) => boolean;
  write: (chunk: string) => void;
  pollMs?: number;
}

export async function runJobsLogs(
  options: JobLogCommandOptions,
): Promise<JobsCommandResult> {
  const result = await readJobLog(toJobLogRequest(options));
  return renderJobLog(result, options.json);
}

export async function streamJobsAttach(
  options: JobAttachStreamCommandOptions,
): Promise<JobsCommandResult> {
  const result = await streamJobLog(toStreamJobLogRequest(options));
  return renderStreamJobLogResult(result, options.json, options.write);
}

function toJobLogRequest(options: JobLogCommandOptions): JobLogRequest {
  return {
    cwd: options.cwd,
    jobId: options.jobId,
  };
}

function toStreamJobLogRequest(
  options: JobAttachStreamCommandOptions,
): StreamJobLogRequest {
  return {
    cwd: options.cwd,
    jobId: options.jobId,
    write: options.write,
    pollMs: options.pollMs,
    now: options.now,
    isPidAlive: options.isPidAlive,
  };
}
