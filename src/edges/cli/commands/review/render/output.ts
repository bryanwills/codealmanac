import type { ReviewCommandOutput } from "./types.js";

export function ok(stdout: string): ReviewCommandOutput {
  return { stdout, stderr: "", exitCode: 0 };
}
