import type { TranscriptCandidate } from "../../shared/transcripts.js";
import { listJobProviderSessionIds } from "../jobs/index.js";

export async function isInternalAlmanacSession(
  candidate: TranscriptCandidate,
  cache: Map<string, Set<string>>,
): Promise<boolean> {
  let ids = cache.get(candidate.repoRoot);
  if (ids === undefined) {
    ids = await listJobProviderSessionIds(candidate.repoRoot);
    cache.set(candidate.repoRoot, ids);
  }
  return ids.has(candidate.sessionId);
}
