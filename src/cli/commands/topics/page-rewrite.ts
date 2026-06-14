import { readFile } from "node:fs/promises";

import fg from "fast-glob";

import {
  applyTopicsTransform,
  rewritePageTopics,
} from "../../../wiki/topics/frontmatter-rewrite.js";
import { wikiPageRoots } from "../../../wiki/locations.js";

/**
 * Apply a `topic-list transform` to every markdown file under `docs/almanac`
 * whose frontmatter contains a relevant topic. Returns the number of
 * files actually changed.
 *
 * We glob page files ourselves (not the DB) so this works even on a
 * stale index — `rename` and `delete` run the indexer AFTER mutation,
 * and we don't want the scan to miss a page that was just modified.
 */
export async function rewriteTopicOnPages(
  repoRoot: string,
  transform: (topics: string[]) => string[],
): Promise<number> {
  let changed = 0;
  for (const root of wikiPageRoots(repoRoot)) {
    const files = await fg("**/*.md", {
      cwd: root.dir,
      absolute: true,
      onlyFiles: true,
    });
    for (const filePath of files) {
      // Cheap read → in-memory check. Skip files that wouldn't be
      // changed so we don't bump their mtime.
      const raw = await readFile(filePath, "utf8");
      const applied = applyTopicsTransform(raw, transform);
      if (!applied.changed) continue;
      await rewritePageTopics(filePath, transform);
      changed += 1;
    }
  }
  return changed;
}
