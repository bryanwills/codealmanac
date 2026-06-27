import { appendFile, mkdir, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

import type { JobLogEntry } from "../../jobs/log-entry.js";

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
