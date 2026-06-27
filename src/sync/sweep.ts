import { readFile } from "node:fs/promises";

import type { SessionCandidate, SweepApp } from "./discovery/index.js";
import {
  type SyncLedger,
  countLines,
  syncCursor,
  freshLedgerEntry,
  ledgerKey,
  reconcileLedger,
  sha256,
} from "./ledger.js";
import {
  loadLedgerForRepo,
  writeLedger,
} from "../stores/sync/ledger.js";
import { acquireRepoSyncLock, releaseRepoSyncLock } from "../stores/sync/lock.js";
import { listJobRecords } from "../jobs/index.js";

export interface SyncStarted {
  app: SweepApp;
  sessionId: string;
  transcriptPath: string;
  repoRoot: string;
  jobId: string;
  fromLine: number;
  toLine: number;
}

export interface SyncReady {
  app: SweepApp;
  sessionId: string;
  transcriptPath: string;
  repoRoot: string;
  fromLine: number;
  toLine: number;
}

export interface SyncSkipped {
  app?: SweepApp;
  sessionId?: string;
  transcriptPath: string;
  repoRoot?: string;
  reason: string;
}

export interface SyncSummary {
  mode: "sync" | "status";
  scanned: number;
  eligible: number;
  syncSince: string | null;
  ready: SyncReady[];
  started: SyncStarted[];
  skipped: SyncSkipped[];
  needsAttention: SyncSkipped[];
}

export interface StartSyncAbsorbArgs {
  candidate: SessionCandidate;
  contextNote: string;
}

export type StartSyncAbsorbResult =
  | { ok: true; jobId: string }
  | { ok: false; error: string };

export type StartSyncAbsorbFn = (
  args: StartSyncAbsorbArgs,
) => Promise<StartSyncAbsorbResult>;

interface TranscriptSnapshot {
  content: Buffer;
  currentSize: number;
  currentLine: number;
}

type TranscriptReadResult =
  | { ok: true; snapshot: TranscriptSnapshot }
  | { ok: false; reason: string };

type SyncCursorDecision =
  | { kind: "skip"; reason: string }
  | { kind: "needs_attention"; reason: string; entry: ReturnType<typeof markPrefixMismatch> }
  | { kind: "ready"; fromLine: number; toLine: number };

export async function executeSyncSweep(args: {
  candidates: SessionCandidate[];
  syncSince: Date | null;
  quietMs: number;
  mode: "sync" | "status";
  now: Date;
  startAbsorb: StartSyncAbsorbFn;
}): Promise<SyncSummary> {
  const summary: SyncSummary = {
    mode: args.mode,
    scanned: args.candidates.length,
    eligible: 0,
    syncSince: args.syncSince?.toISOString() ?? null,
    ready: [],
    started: [],
    skipped: [],
    needsAttention: [],
  };

  const ledgers = new Map<string, SyncLedger>();
  const internalSessionIds = new Map<string, Set<string>>();
  const heldLocks = new Set<string>();
  try {
    for (const candidate of args.candidates) {
      const eligibilitySkip = candidateEligibility(candidate, args);
      if (eligibilitySkip !== null) {
        summary.skipped.push(eligibilitySkip);
        continue;
      }

      if (await isInternalAlmanacSession(candidate, internalSessionIds)) {
        summary.skipped.push(skip(candidate, "internal-almanac-session"));
        continue;
      }

      if (args.mode === "sync" && !heldLocks.has(candidate.repoRoot)) {
        const locked = await acquireRepoSyncLock(candidate.repoRoot, args.now);
        if (!locked) {
          summary.skipped.push(skip(candidate, "sync-already-running"));
          continue;
        }
        heldLocks.add(candidate.repoRoot);
      }

      const ledger = await loadLedgerForRepo(candidate.repoRoot, ledgers);
      await reconcileLedger(candidate.repoRoot, ledger, args.now);
      const key = ledgerKey(candidate);

      const transcript = await readTranscriptSnapshot(candidate);
      if (!transcript.ok) {
        summary.needsAttention.push(skip(candidate, transcript.reason));
        continue;
      }
      const entry = ledger.sessions[key] ??
        freshLedgerEntry(candidate, transcript.snapshot.content, args.syncSince);

      const decision = evaluateSyncCursor(entry, transcript.snapshot);
      ledger.sessions[key] = decision.kind === "needs_attention"
        ? decision.entry
        : entry;

      if (decision.kind === "skip") {
        summary.skipped.push(skip(candidate, decision.reason));
        continue;
      }
      if (decision.kind === "needs_attention") {
        summary.needsAttention.push(skip(candidate, decision.reason));
        continue;
      }

      summary.eligible += 1;
      if (args.mode === "status") {
        summary.ready.push(readySummary(candidate, decision));
        continue;
      }

      const enqueue = await enqueueAbsorb({
        candidate,
        entry,
        decision,
        snapshot: transcript.snapshot,
        now: args.now,
        startAbsorb: args.startAbsorb,
      });
      if (!enqueue.ok) {
        ledger.sessions[key] = enqueue.entry;
        summary.needsAttention.push(skip(candidate, enqueue.reason));
        await writeLedger(candidate.repoRoot, ledger, args.now);
        continue;
      }
      ledger.sessions[key] = enqueue.entry;
      await writeLedger(candidate.repoRoot, ledger, args.now);
      summary.started.push(startedSummary(candidate, enqueue.jobId, decision));
    }

    if (args.mode === "sync") {
      for (const [repoRoot, ledger] of ledgers) {
        await writeLedger(repoRoot, ledger, args.now);
      }
    }
  } finally {
    await Promise.all([...heldLocks].map(releaseRepoSyncLock));
  }

  return summary;
}

async function isInternalAlmanacSession(
  candidate: SessionCandidate,
  cache: Map<string, Set<string>>,
): Promise<boolean> {
  let ids = cache.get(candidate.repoRoot);
  if (ids === undefined) {
    ids = new Set(
      (await listJobRecords(candidate.repoRoot))
        .map((record) => record.providerSessionId)
        .filter((id): id is string => typeof id === "string" && id.length > 0),
    );
    cache.set(candidate.repoRoot, ids);
  }
  return ids.has(candidate.sessionId);
}

function candidateEligibility(
  candidate: SessionCandidate,
  args: {
    syncSince: Date | null;
    quietMs: number;
    now: Date;
  },
): SyncSkipped | null {
  if (args.syncSince !== null && candidate.mtimeMs < args.syncSince.getTime()) {
    return skip(candidate, "before-automation-activation");
  }

  const quietForMs = args.now.getTime() - candidate.mtimeMs;
  if (quietForMs < args.quietMs) {
    return skip(candidate, "quiet-window");
  }
  return null;
}

async function readTranscriptSnapshot(
  candidate: SessionCandidate,
): Promise<TranscriptReadResult> {
  try {
    const content = await readFile(candidate.transcriptPath);
    return {
      ok: true,
      snapshot: {
        content,
        currentSize: content.length,
        currentLine: countLines(content.toString("utf8")),
      },
    };
  } catch (err: unknown) {
    const reason = `read-failed: ${err instanceof Error ? err.message : String(err)}`;
    return { ok: false, reason };
  }
}

function evaluateSyncCursor(
  entry: SyncLedger["sessions"][string],
  snapshot: TranscriptSnapshot,
): SyncCursorDecision {
  if (entry.status === "pending") {
    return { kind: "skip", reason: "sync-already-pending" };
  }

  if (snapshot.currentSize <= entry.lastAbsorbedSize) {
    return { kind: "skip", reason: "unchanged" };
  }

  const prefixHash = sha256(snapshot.content.subarray(0, entry.lastAbsorbedSize));
  if (prefixHash !== entry.lastAbsorbedPrefixHash) {
    return {
      kind: "needs_attention",
      reason: "prefix-mismatch",
      entry: markPrefixMismatch(entry),
    };
  }

  return {
    kind: "ready",
    fromLine: entry.lastAbsorbedLine + 1,
    toLine: snapshot.currentLine,
  };
}

function markPrefixMismatch(
  entry: SyncLedger["sessions"][string],
): SyncLedger["sessions"][string] {
  return {
    ...entry,
    status: "needs_attention",
    lastError: "transcript prefix no longer matches ledger cursor",
  };
}

async function enqueueAbsorb(args: {
  candidate: SessionCandidate;
  entry: SyncLedger["sessions"][string];
  decision: Extract<SyncCursorDecision, { kind: "ready" }>;
  snapshot: TranscriptSnapshot;
  now: Date;
  startAbsorb: StartSyncAbsorbFn;
}): Promise<
  | { ok: true; jobId: string; entry: SyncLedger["sessions"][string] }
  | { ok: false; reason: string; entry: SyncLedger["sessions"][string] }
> {
  const result = await args.startAbsorb({
    candidate: args.candidate,
    contextNote: cursorContext({
      candidate: args.candidate,
      fromLine: args.decision.fromLine,
      lastAbsorbedLine: args.entry.lastAbsorbedLine,
      lastAbsorbedSize: args.entry.lastAbsorbedSize,
    }),
  });
  if (!result.ok) {
    return {
      ok: false,
      reason: "absorb-start-failed",
      entry: {
        ...args.entry,
        status: "failed",
        lastError: result.error,
      },
    };
  }
  const pendingCursor = syncCursor(args.snapshot.content, args.snapshot.currentLine);
  return {
    ok: true,
    jobId: result.jobId,
    entry: {
      ...args.entry,
      status: "pending",
      pendingToSize: pendingCursor.size,
      pendingToLine: pendingCursor.line,
      pendingPrefixHash: pendingCursor.prefixHash,
      pendingJobId: result.jobId,
      pendingStartedAt: args.now.toISOString(),
      lastJobId: result.jobId,
      lastError: undefined,
    },
  };
}

function startedSummary(
  candidate: SessionCandidate,
  jobId: string,
  decision: Extract<SyncCursorDecision, { kind: "ready" }>,
): SyncStarted {
  return {
    app: candidate.app,
    sessionId: candidate.sessionId,
    transcriptPath: candidate.transcriptPath,
    repoRoot: candidate.repoRoot,
    jobId,
    fromLine: decision.fromLine,
    toLine: decision.toLine,
  };
}

function readySummary(
  candidate: SessionCandidate,
  decision: Extract<SyncCursorDecision, { kind: "ready" }>,
): SyncReady {
  return {
    app: candidate.app,
    sessionId: candidate.sessionId,
    transcriptPath: candidate.transcriptPath,
    repoRoot: candidate.repoRoot,
    fromLine: decision.fromLine,
    toLine: decision.toLine,
  };
}

function cursorContext(args: {
  candidate: SessionCandidate;
  fromLine: number;
  lastAbsorbedLine: number;
  lastAbsorbedSize: number;
}): string {
  return [
    "Scheduled sync cursor:",
    `- App: ${args.candidate.app}`,
    `- Session id: ${args.candidate.sessionId}`,
    `- Transcript: ${args.candidate.transcriptPath}`,
    `- Previously absorbed through line: ${args.lastAbsorbedLine}`,
    `- Previously absorbed through byte: ${args.lastAbsorbedSize}`,
    `- Focus on line ${args.fromLine} onward.`,
    "- You may inspect earlier lines only for context.",
    "- Do not re-document decisions already absorbed unless newer lines amend, invalidate, or add important nuance to them.",
  ].join("\n");
}

function skip(candidate: Partial<SessionCandidate> & { transcriptPath: string }, reason: string): SyncSkipped {
  return {
    app: candidate.app,
    sessionId: candidate.sessionId,
    transcriptPath: candidate.transcriptPath,
    repoRoot: candidate.repoRoot,
    reason,
  };
}
