import { readFile } from "node:fs/promises";

import { objectField, parseJsonObject, stringField } from "./jsonl.js";

export interface TranscriptSnapshot {
  content: Buffer;
  currentSize: number;
  currentLine: number;
}

export interface TranscriptCursorBoundary {
  size: number;
  line: number;
}

export type TranscriptReadResult =
  | { ok: true; snapshot: TranscriptSnapshot }
  | { ok: false; reason: string };

export async function readTranscriptSnapshot(
  transcriptPath: string,
): Promise<TranscriptReadResult> {
  try {
    const content = await readFile(transcriptPath);
    return {
      ok: true,
      snapshot: {
        content,
        currentSize: content.length,
        currentLine: countTranscriptLines(content.toString("utf8")),
      },
    };
  } catch (err: unknown) {
    const reason = `read-failed: ${err instanceof Error ? err.message : String(err)}`;
    return { ok: false, reason };
  }
}

export function transcriptCursorForSince(
  content: Buffer,
  since: Date,
): TranscriptCursorBoundary {
  const text = content.toString("utf8");
  let offset = 0;
  let line = 0;
  for (const rawLine of text.split(/(?<=\n)/)) {
    if (rawLine.length === 0) continue;
    const lineWithoutNewline = rawLine.replace(/\r?\n$/, "");
    const timestamp = transcriptLineTimestamp(lineWithoutNewline);
    if (timestamp !== null && timestamp >= since.getTime()) {
      return { size: offset, line };
    }
    offset += Buffer.byteLength(rawLine);
    line += 1;
  }
  return { size: content.length, line };
}

function countTranscriptLines(content: string): number {
  if (content.length === 0) return 0;
  const matches = content.match(/\n/g);
  return (matches?.length ?? 0) + (content.endsWith("\n") ? 0 : 1);
}

function transcriptLineTimestamp(line: string): number | null {
  const parsed = parseJsonObject(line);
  if (parsed === null) return null;
  const rawTimestamp = stringField(parsed, "timestamp") ??
    stringField(objectField(parsed, "payload") ?? {}, "timestamp");
  if (rawTimestamp === undefined) return null;
  const ms = Date.parse(rawTimestamp);
  return Number.isFinite(ms) ? ms : null;
}
