import { renderError, renderOutcome } from "../outcome.js";
import {
  runSyncWorkflow,
  type SyncWorkflowOptions,
  type SyncWorkflowSummary,
} from "../../services/sync/index.js";

export interface SyncCommandOptions {
  cwd: string;
  mode?: "sync" | "status";
  from?: string;
  quiet?: string;
  using?: string;
  json?: boolean;
  now?: Date;
  homeDir?: string;
  configPath?: string;
  startBackground?: SyncWorkflowOptions["startBackground"];
}

export interface SyncCommandResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export async function runSyncCommand(
  options: SyncCommandOptions,
): Promise<SyncCommandResult> {
  const result = await runSyncWorkflow(toSyncWorkflowOptions(options));
  if (result.status === "invalid") {
    return renderError(result.error, { json: options.json });
  }
  return renderSyncSummary(result.summary, options.json);
}

function renderSyncSummary(
  summary: SyncWorkflowSummary,
  json: boolean | undefined,
): SyncCommandResult {
  const statusMode = summary.mode === "status";
  const action = statusMode ? "ready" : "started";
  const actionCount = statusMode ? summary.ready.length : summary.started.length;
  const message = statusMode ? "sync status completed" : "sync completed";
  const lines = [
    statusMode ? "sync status:" : "sync:",
    `  scanned: ${summary.scanned}`,
    ...(summary.syncSince !== null
      ? [`  syncing transcripts after: ${summary.syncSince}`]
      : []),
    `  eligible: ${summary.eligible}`,
    `  ${action}: ${actionCount}`,
    `  skipped: ${summary.skipped.length}`,
    `  needs attention: ${summary.needsAttention.length}`,
  ];
  for (const ready of summary.ready) {
    lines.push(
      `  - ready ${ready.app} ${ready.sessionId}: ` +
        `lines ${ready.fromLine}-${ready.toLine}`,
    );
  }
  for (const started of summary.started) {
    lines.push(
      `  - started ${started.app} ${started.sessionId}: ${started.jobId} ` +
        `(lines ${started.fromLine}-${started.toLine})`,
    );
  }
  for (const item of summary.needsAttention) {
    lines.push(`  - needs attention ${item.transcriptPath}: ${item.reason}`);
  }
  return renderOutcome(
    {
      type: "success",
      message,
      data: { summary },
    },
    { json, stdout: `${lines.join("\n")}\n` },
  );
}

function toSyncWorkflowOptions(
  options: SyncCommandOptions,
): SyncWorkflowOptions {
  return {
    mode: options.mode,
    from: options.from,
    quiet: options.quiet,
    using: options.using,
    now: options.now,
    homeDir: options.homeDir,
    configPath: options.configPath,
    startBackground: options.startBackground,
  };
}
