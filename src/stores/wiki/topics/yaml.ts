import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";

import { writeTextFileAtomically } from "../../atomic-write.js";
import { topicsYamlPath } from "./paths.js";
import {
  formatTopicsFileContent,
  parseTopicsFileContent,
} from "./codec.js";
import type { TopicsFile } from "./types.js";

export function hasTopicsFile(repoRoot: string): boolean {
  return existsSync(topicsYamlPath(repoRoot));
}

/**
 * Load `.almanac/topics.yaml` into a `TopicsFile`. A missing file is not
 * an error — it's the first-run state, which we treat as "no topic
 * metadata, only whatever the pages declare in frontmatter". Malformed
 * YAML IS an error; we surface it rather than silently clobbering the
 * user's committed source of truth.
 *
 * The return shape is always normalized — callers don't have to guard
 * for missing `topics` key, wrong types, or absent `parents` arrays.
 */
export async function loadTopicsFile(path: string): Promise<TopicsFile> {
  if (!existsSync(path)) {
    return { topics: [] };
  }
  let raw: string;
  try {
    raw = await readFile(path, "utf8");
  } catch (err: unknown) {
    if (isNodeError(err) && err.code === "ENOENT") {
      return { topics: [] };
    }
    throw err;
  }

  return parseTopicsFileContent(raw, path);
}

/**
 * Write a `TopicsFile` atomically — tmp file + rename, same pattern as
 * the registry. A half-written topics.yaml would corrupt the user's
 * committed source of truth, so we never write in place.
 *
 * Ordering: topics are sorted by slug for stable diffs. Parents within
 * each entry stay in the order the caller passed them (semantically an
 * ordered list — topics.yaml is the place a user can visibly reason
 * about "primary parent first", even though SQLite treats them as a
 * set).
 *
 * We emit a leading comment so first-time readers know the file is
 * edited by the CLI and what its role is.
 */
export async function writeTopicsFile(
  path: string,
  file: TopicsFile,
): Promise<void> {
  await writeTextFileAtomically(path, formatTopicsFileContent(file));
}

function isNodeError(err: unknown): err is NodeJS.ErrnoException {
  return err instanceof Error && "code" in err;
}
