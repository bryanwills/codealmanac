import type { TranscriptCandidate } from "../../shared/transcripts.js";
import { syncSkippedSummary, type SyncSkipped } from "./sweep-results.js";

export function syncCandidateEligibility(
  candidate: TranscriptCandidate,
  args: {
    syncSince: Date | null;
    quietMs: number;
    now: Date;
  },
): SyncSkipped | null {
  if (args.syncSince !== null && candidate.mtimeMs < args.syncSince.getTime()) {
    return syncSkippedSummary(candidate, "before-automation-activation");
  }

  const quietForMs = args.now.getTime() - candidate.mtimeMs;
  if (quietForMs < args.quietMs) {
    return syncSkippedSummary(candidate, "quiet-window");
  }
  return null;
}
