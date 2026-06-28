import { appendFile, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

import type { JobLogEntry } from "./log-entry.js";
import { resolveJobLogPath } from "./records.js";

export async function initializeJobLog(path: string): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, "", "utf8");
}

export async function appendJobLogEntry(
  path: string,
  entry: JobLogEntry,
): Promise<void> {
  await appendFile(path, `${JSON.stringify(entry)}\n`, "utf8");
}

export async function readJobLogContents(
  repoRoot: string,
  jobId: string,
): Promise<string> {
  return readFile(await resolveJobLogPath(repoRoot, jobId), "utf8");
}

export async function readJobLogChunk(
  repoRoot: string,
  jobId: string,
  offset: number,
): Promise<{ contents: string; nextOffset: number }> {
  const text = await readJobLogContents(repoRoot, jobId);
  if (text.length <= offset) {
    return { contents: "", nextOffset: offset };
  }
  return { contents: text.slice(offset), nextOffset: text.length };
}
