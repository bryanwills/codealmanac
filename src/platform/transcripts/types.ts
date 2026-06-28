export type TranscriptSourceApp = "claude" | "codex";

export interface TranscriptCandidate {
  app: TranscriptSourceApp;
  sessionId: string;
  transcriptPath: string;
  cwd: string;
  repoRoot: string;
  mtimeMs: number;
  sizeBytes: number;
}
