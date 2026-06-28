import { discoverClaude } from "./claude.js";
import { discoverCodex } from "./codex.js";
import type { TranscriptCandidate, TranscriptSourceApp } from "./types.js";

export type { TranscriptCandidate, TranscriptSourceApp } from "./types.js";

export async function discoverTranscriptCandidates(args: {
  apps: TranscriptSourceApp[];
  home: string;
  claudeProjectsDir?: string;
  codexSessionsDir?: string;
}): Promise<TranscriptCandidate[]> {
  const out: TranscriptCandidate[] = [];
  if (args.apps.includes("claude")) {
    out.push(...await discoverClaude(args.home, args.claudeProjectsDir));
  }
  if (args.apps.includes("codex")) {
    out.push(...await discoverCodex(args.home, args.codexSessionsDir));
  }
  return out;
}
