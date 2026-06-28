import { listJobs, readJob } from "../../../../services/jobs/index.js";
import type {
  JobRequest,
  JobsRequest,
} from "../../../../services/jobs/index.js";
import {
  renderJobsListResult,
  renderJobsShowResult,
  type JobsCommandResult,
} from "./render.js";

export interface JobsListCommandOptions {
  cwd: string;
  json?: boolean;
  now?: () => Date;
  isPidAlive: (pid: number) => boolean;
}

export interface JobByIdCommandOptions {
  cwd: string;
  jobId: string;
  json?: boolean;
  now?: () => Date;
  isPidAlive: (pid: number) => boolean;
}

export async function runJobsList(
  options: JobsListCommandOptions,
): Promise<JobsCommandResult> {
  return renderJobsListResult(
    await listJobs(toJobsRequest(options)),
    options.json,
  );
}

export async function runJobsShow(
  options: JobByIdCommandOptions,
): Promise<JobsCommandResult> {
  return renderJobsShowResult(await readJob(toJobRequest(options)), options.json);
}

function toJobsRequest(options: JobsListCommandOptions): JobsRequest {
  return {
    cwd: options.cwd,
    now: options.now,
    isPidAlive: options.isPidAlive,
  };
}

function toJobRequest(options: JobByIdCommandOptions): JobRequest {
  return {
    cwd: options.cwd,
    jobId: options.jobId,
    now: options.now,
    isPidAlive: options.isPidAlive,
  };
}
