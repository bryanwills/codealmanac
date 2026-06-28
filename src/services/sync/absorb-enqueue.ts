import type {
  TranscriptCandidate,
  TranscriptSnapshot,
} from "../../shared/transcripts.js";
import type { LedgerEntry } from "./ledger.js";
import {
  failedLedgerEntry,
  pendingLedgerEntry,
  type SyncCursorDecision,
} from "./transcript-cursor.js";

export interface StartSyncAbsorbArgs {
  candidate: TranscriptCandidate;
  contextNote: string;
}

export type StartSyncAbsorbResult =
  | { ok: true; jobId: string }
  | { ok: false; error: string };

export type StartSyncAbsorbFn = (
  args: StartSyncAbsorbArgs,
) => Promise<StartSyncAbsorbResult>;

export async function enqueueSyncAbsorb(args: {
  candidate: TranscriptCandidate;
  entry: LedgerEntry;
  decision: Extract<SyncCursorDecision, { kind: "ready" }>;
  snapshot: TranscriptSnapshot;
  now: Date;
  startAbsorb: StartSyncAbsorbFn;
}): Promise<
  | { ok: true; jobId: string; entry: LedgerEntry }
  | { ok: false; reason: string; entry: LedgerEntry }
> {
  const result = await args.startAbsorb({
    candidate: args.candidate,
    contextNote: syncCursorContext({
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
      entry: failedLedgerEntry(args.entry, result.error),
    };
  }
  return {
    ok: true,
    jobId: result.jobId,
    entry: pendingLedgerEntry({
      entry: args.entry,
      snapshot: args.snapshot,
      jobId: result.jobId,
      now: args.now,
    }),
  };
}

function syncCursorContext(args: {
  candidate: TranscriptCandidate;
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
    "- Do not re-document decisions already absorbed unless newer lines amend, " +
      "invalidate, or add important nuance to them.",
  ].join("\n");
}
