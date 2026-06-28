import { existsSync } from "node:fs";
import { join } from "node:path";

import type Database from "better-sqlite3";

import { inPageScope, type HealthScope } from "./scope.js";

export interface CrossWikiLinkRef {
  source_slug: string;
  target_wiki: string;
  target_slug: string;
}

/**
 * `file_refs` whose target paths no longer exist on disk. We `stat`
 * each referenced path, relative to the repo root, and report misses.
 *
 * Only checks active pages; archived pages are allowed to reference
 * files that have since been deleted.
 */
export async function findDeadRefs(
  db: Database.Database,
  scope: HealthScope,
  repoRoot: string,
): Promise<{ slug: string; path: string }[]> {
  const rows = db
    .prepare<
      [],
      { slug: string; path: string; original_path: string; is_dir: number }
    >(
      `SELECT p.slug, r.path, r.original_path, r.is_dir
       FROM file_refs r
       JOIN pages p ON p.slug = r.page_slug
       WHERE p.archived_at IS NULL
       ORDER BY p.slug, r.path`,
    )
    .all();
  const out: { slug: string; path: string }[] = [];
  for (const r of rows) {
    if (!inPageScope(scope, r.slug)) continue;
    if (!existsSync(join(repoRoot, r.original_path))) {
      out.push({ slug: r.slug, path: r.original_path });
    }
  }
  return out;
}

/**
 * Wikilinks whose target slug has no row in `pages`.
 */
export function findBrokenLinks(
  db: Database.Database,
  scope: HealthScope,
): { source_slug: string; target_slug: string }[] {
  const rows = db
    .prepare<[], { source_slug: string; target_slug: string }>(
      `SELECT w.source_slug, w.target_slug
       FROM wikilinks w
       JOIN pages src ON src.slug = w.source_slug
       LEFT JOIN pages tgt ON tgt.slug = w.target_slug
       WHERE tgt.slug IS NULL AND src.archived_at IS NULL
       ORDER BY w.source_slug, w.target_slug`,
    )
    .all();
  return rows.filter((r) => inPageScope(scope, r.source_slug));
}

/**
 * Indexed cross-wiki links from active pages.
 */
export function findCrossWikiLinks(
  db: Database.Database,
  scope: HealthScope,
): CrossWikiLinkRef[] {
  const rows = db
    .prepare<
      [],
      CrossWikiLinkRef
    >(
      `SELECT x.source_slug, x.target_wiki, x.target_slug
       FROM cross_wiki_links x
       JOIN pages src ON src.slug = x.source_slug
       WHERE src.archived_at IS NULL
       ORDER BY x.source_slug, x.target_wiki, x.target_slug`,
    )
    .all();
  return rows.filter((r) => inPageScope(scope, r.source_slug));
}
