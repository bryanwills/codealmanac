import type { CommandResult } from "../helpers.js";
import { renderError, renderOutcome } from "../outcome.js";
import {
  runAbsorbOperationWorkflow,
  runGardenOperationWorkflow,
  runInitOperationWorkflow,
  type AbsorbOperationWorkflowOptions,
  type GardenOperationWorkflowOptions,
  type InitOperationWorkflowOptions,
  type LifecycleOperationWorkflowResult,
  type OperationRunResult,
} from "../../services/lifecycle/index.js";

export { parseUsing } from "../../services/lifecycle/index.js";

export interface InitCommandOptions extends InitOperationWorkflowOptions {
  cwd: string;
  json?: boolean;
}

export interface AbsorbCommandOptions extends AbsorbOperationWorkflowOptions {
  cwd: string;
  inputs: string[];
  json?: boolean;
}

export interface GardenCommandOptions extends GardenOperationWorkflowOptions {
  cwd: string;
  json?: boolean;
}

export async function runInitCommand(
  options: InitCommandOptions,
): Promise<CommandResult> {
  return renderWorkflowResult(
    await runInitOperationWorkflow(options),
    options.json,
  );
}

export async function runAbsorbCommand(
  options: AbsorbCommandOptions,
): Promise<CommandResult> {
  return renderWorkflowResult(
    await runAbsorbOperationWorkflow(options),
    options.json,
  );
}

export const runIngestCommand = runAbsorbCommand;

export async function runGardenCommand(
  options: GardenCommandOptions,
): Promise<CommandResult> {
  return renderWorkflowResult(
    await runGardenOperationWorkflow(options),
    options.json,
  );
}

function renderOperationResult(
  operation: string,
  result: OperationRunResult,
  json: boolean | undefined,
): CommandResult {
  const record = result.background?.record ?? result.foreground?.record;
  const status = record?.status;
  const foregroundResult = result.foreground?.result;
  if (
    result.mode === "foreground" &&
    (foregroundResult?.success === false || status === "failed")
  ) {
    const failure = foregroundResult?.failure ?? record?.failure;
    return renderOutcome(
      {
        type: "error",
        message: renderOperationFailureMessage({
          operation,
          jobId: result.jobId,
          error: foregroundResult?.error,
          failure,
        }),
        data: {
          operation,
          jobId: result.jobId,
          mode: result.mode,
          status,
          pid: record?.pid,
          logPath: record?.logPath,
          error: foregroundResult?.error,
          failure,
        },
      },
      { json },
    );
  }
  const message = result.mode === "background"
    ? `${operation} started: ${result.jobId}`
    : `${operation} finished: ${result.jobId}`;
  const stdout = operation === "init" && result.mode === "foreground"
    ? `${message}\nBrowse the wiki: almanac serve\n`
    : undefined;

  return renderOutcome(
    {
      type: "success",
      message,
      data: {
        operation,
        jobId: result.jobId,
        mode: result.mode,
        status,
        pid: record?.pid,
        logPath: record?.logPath,
      },
    },
    { json, stdout },
  );
}

function renderOperationFailureMessage(args: {
  operation: string;
  jobId: string;
  error?: string;
  failure?: import("../../harness/events.js").HarnessFailure;
}): string {
  const lines = [`${args.operation} failed: ${args.jobId}`];
  if (args.failure !== undefined) {
    lines.push(`Reason: ${args.failure.message}`);
    if (args.failure.fix !== undefined) lines.push(`Fix: ${args.failure.fix}`);
    return lines.join("\n");
  }
  if (args.error !== undefined) lines[0] += `: ${args.error}`;
  return lines.join("\n");
}

function renderOperationError(
  err: unknown,
  json: boolean | undefined,
): CommandResult {
  return renderError(err, { json });
}

function jsonForegroundError(json: boolean | undefined): CommandResult {
  return renderOutcome({
    type: "error",
    message: "--json is only supported for background job start responses",
  }, { json });
}

function renderWorkflowResult(
  result: LifecycleOperationWorkflowResult,
  json: boolean | undefined,
): CommandResult {
  switch (result.status) {
    case "completed":
      return renderOperationResult(result.operation, result.result, json);
    case "json-foreground-unsupported":
      return jsonForegroundError(json);
    case "failed":
      return renderOperationError(result.error, json);
  }
}
