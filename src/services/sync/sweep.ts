import {
  type TranscriptCandidate,
  type TranscriptReadResult,
} from "../../shared/transcripts.js";
import {
  type SyncLedger,
  freshLedgerEntry,
  ledgerKey,
  reconcileLedger,
} from "./ledger.js";
import { evaluateSyncCursor } from "./transcript-cursor.js";
import {
  type SyncSummary,
  emptySyncSummary,
  syncReadySummary,
  syncSkippedSummary,
  syncStartedSummary,
} from "./sweep-results.js";
import type { IsPidAlive } from "../../shared/pid-liveness.js";
import {
  enqueueSyncAbsorb,
  type StartSyncAbsorbFn,
} from "./absorb-enqueue.js";
import { syncCandidateEligibility } from "./candidate-eligibility.js";
import { isInternalAlmanacSession } from "./internal-sessions.js";
import {
  loadLedgerForRepo,
  writeLedger,
} from "../../stores/sync/ledger.js";
import { acquireRepoSyncLock, releaseRepoSyncLock } from "../../stores/sync/lock.js";

export type ReadSyncTranscriptSnapshotFn = (
  transcriptPath: string,
) => Promise<TranscriptReadResult>;

export async function executeSyncSweep(args: {
  candidates: TranscriptCandidate[];
  syncSince: Date | null;
  quietMs: number;
  mode: "sync" | "status";
  now: Date;
  lockOwnerPid: number;
  isPidAlive: IsPidAlive;
  readTranscriptSnapshot: ReadSyncTranscriptSnapshotFn;
  startAbsorb: StartSyncAbsorbFn;
}): Promise<SyncSummary> {
  const summary = emptySyncSummary({
    mode: args.mode,
    scanned: args.candidates.length,
    syncSince: args.syncSince,
  });

  const ledgers = new Map<string, SyncLedger>();
  const internalSessionIds = new Map<string, Set<string>>();
  const heldLocks = new Set<string>();
  try {
    for (const candidate of args.candidates) {
      const eligibilitySkip = syncCandidateEligibility(candidate, args);
      if (eligibilitySkip !== null) {
        summary.skipped.push(eligibilitySkip);
        continue;
      }

      if (await isInternalAlmanacSession(candidate, internalSessionIds)) {
        summary.skipped.push(
          syncSkippedSummary(candidate, "internal-almanac-session"),
        );
        continue;
      }

      if (args.mode === "sync" && !heldLocks.has(candidate.repoRoot)) {
        const locked = await acquireRepoSyncLock(candidate.repoRoot, args.now, {
          ownerPid: args.lockOwnerPid,
          isPidAlive: args.isPidAlive,
        });
        if (!locked) {
          summary.skipped.push(
            syncSkippedSummary(candidate, "sync-already-running"),
          );
          continue;
        }
        heldLocks.add(candidate.repoRoot);
      }

      const ledger = await loadLedgerForRepo(candidate.repoRoot, ledgers);
      await reconcileLedger(candidate.repoRoot, ledger, args.now);
      const key = ledgerKey(candidate);

      const transcript = await args.readTranscriptSnapshot(
        candidate.transcriptPath,
      );
      if (!transcript.ok) {
        summary.needsAttention.push(
          syncSkippedSummary(candidate, transcript.reason),
        );
        continue;
      }
      const entry = ledger.sessions[key] ??
        freshLedgerEntry(candidate, transcript.snapshot.content, args.syncSince);

      const decision = evaluateSyncCursor(entry, transcript.snapshot);
      ledger.sessions[key] = decision.kind === "needs_attention"
        ? decision.entry
        : entry;

      if (decision.kind === "skip") {
        summary.skipped.push(syncSkippedSummary(candidate, decision.reason));
        continue;
      }
      if (decision.kind === "needs_attention") {
        summary.needsAttention.push(syncSkippedSummary(candidate, decision.reason));
        continue;
      }

      summary.eligible += 1;
      if (args.mode === "status") {
        summary.ready.push(syncReadySummary(candidate, decision));
        continue;
      }

      const enqueue = await enqueueSyncAbsorb({
        candidate,
        entry,
        decision,
        snapshot: transcript.snapshot,
        now: args.now,
        startAbsorb: args.startAbsorb,
      });
      if (!enqueue.ok) {
        ledger.sessions[key] = enqueue.entry;
        summary.needsAttention.push(
          syncSkippedSummary(candidate, enqueue.reason),
        );
        await writeLedger(candidate.repoRoot, ledger, args.now);
        continue;
      }
      ledger.sessions[key] = enqueue.entry;
      await writeLedger(candidate.repoRoot, ledger, args.now);
      summary.started.push(
        syncStartedSummary(candidate, enqueue.jobId, decision),
      );
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
