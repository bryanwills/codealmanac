import { homedir } from "node:os";

import * as sync from "../../sync/index.js";
import * as operations from "../../operations/index.js";
import type { CommandResult } from "../helpers.js";
import { renderError, renderOutcome } from "../outcome.js";
import { parseDuration } from "../../shared/duration.js";
import { readConfig } from "../../config/index.js";

export interface SyncCommandOptions {
  cwd: string;
  mode?: "sync" | "status";
  from?: string;
  quiet?: string;
  json?: boolean;
  using?: string;
  now?: Date;
  homeDir?: string;
  configPath?: string;
  startBackground?: operations.StartBackgroundJob;
}

const DEFAULT_QUIET = "45m";

export async function runSyncCommand(
  options: SyncCommandOptions,
): Promise<CommandResult> {
  const now = options.now ?? new Date();
  const mode = options.mode ?? "sync";
  const sources = parseSources(options.from);
  if (!sources.ok) return renderError(sources.error, { json: options.json });
  const quiet = parseQuiet(options.quiet ?? DEFAULT_QUIET);
  if (!quiet.ok) return renderError(quiet.error, { json: options.json });

  const home = options.homeDir ?? homedir();
  const syncSince = await readSyncSince(options.configPath);
  const candidates = await sync.discoverCandidates({
    apps: sources.value,
    home,
  });
  const providers = new Map<string, operations.OperationProviderSelection>();

  const summary = await sync.sweep({
    candidates,
    syncSince,
    quietMs: quiet.ms,
    mode,
    now,
    startAbsorb: async ({ candidate, contextNote }) => {
      try {
        const provider = await providerForRepo({
          repoRoot: candidate.repoRoot,
          using: options.using,
          cache: providers,
        });
        const result = await operations.absorb({
          cwd: candidate.repoRoot,
          provider,
          background: true,
          context: syncAbsorbContext({
            app: candidate.app,
            sessionId: candidate.sessionId,
            transcriptPath: candidate.transcriptPath,
            contextNote,
          }),
          targetKind: "session",
          targetPaths: [candidate.transcriptPath],
          startBackground: options.startBackground,
        });
        return { ok: true, jobId: result.jobId };
      } catch (err: unknown) {
        return { ok: false, error: err instanceof Error ? err.message : String(err) };
      }
    },
  });

  return renderSyncSummary(summary, options.json);
}

async function providerForRepo(args: {
  repoRoot: string;
  using?: string;
  cache: Map<string, operations.OperationProviderSelection>;
}): Promise<operations.OperationProviderSelection> {
  const key = `${args.repoRoot}\0${args.using ?? ""}`;
  const cached = args.cache.get(key);
  if (cached !== undefined) return cached;
  const provider = await operations.resolveProvider({
    cwd: args.repoRoot,
    using: args.using,
  });
  args.cache.set(key, provider);
  return provider;
}

function parseSources(value: string | undefined): { ok: true; value: sync.SweepApp[] } | { ok: false; error: Error } {
  if (value === undefined || value.trim().length === 0) {
    return { ok: true, value: ["claude", "codex"] };
  }
  const apps: sync.SweepApp[] = [];
  for (const raw of value.split(",")) {
    const app = raw.trim();
    if (app === "claude" || app === "codex") {
      if (!apps.includes(app)) apps.push(app);
      continue;
    }
    return { ok: false, error: new Error(`invalid --from "${value}" (expected claude,codex)`) };
  }
  return { ok: true, value: apps };
}

function parseQuiet(value: string): { ok: true; ms: number } | { ok: false; error: Error } {
  try {
    return { ok: true, ms: parseDuration(value) * 1000 };
  } catch (err: unknown) {
    return { ok: false, error: err instanceof Error ? err : new Error(String(err)) };
  }
}

async function readSyncSince(configPath: string | undefined): Promise<Date | null> {
  const config = await readConfig(configPath);
  const raw = config.automation.sync_since;
  if (raw === null) return null;
  const ms = Date.parse(raw);
  return Number.isFinite(ms) ? new Date(ms) : null;
}

function renderSyncSummary(
  summary: sync.SyncSummary,
  json: boolean | undefined,
): CommandResult {
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

function syncAbsorbContext(args: {
  app: sync.SweepApp;
  sessionId: string;
  transcriptPath: string;
  contextNote: string;
}): string {
  return [
    "Command context:",
    "- Command: sync",
    "- Input kind: AI coding session transcript",
    `- App: ${args.app}`,
    `- Session id: ${args.sessionId}`,
    `- Transcript: ${args.transcriptPath}`,
    "",
    args.contextNote,
  ].join("\n");
}
