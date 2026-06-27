import { existsSync } from "node:fs";
import { join } from "node:path";

import type Database from "better-sqlite3";

import { findEntry } from "../../stores/wiki-registry/index.js";
import { inPageScope, type HealthScope } from "./scope.js";

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
 * Cross-wiki links whose target wiki is unregistered or unreachable.
 */
export async function findBrokenXwiki(
  db: Database.Database,
  scope: HealthScope,
): Promise<{ source_slug: string; target_wiki: string; target_slug: string }[]> {
  const rows = db
    .prepare<
      [],
      { source_slug: string; target_wiki: string; target_slug: string }
    >(
      `SELECT x.source_slug, x.target_wiki, x.target_slug
       FROM cross_wiki_links x
       JOIN pages src ON src.slug = x.source_slug
       WHERE src.archived_at IS NULL
       ORDER BY x.source_slug, x.target_wiki, x.target_slug`,
    )
    .all();
  const out: { source_slug: string; target_wiki: string; target_slug: string }[] = [];
  const reachableCache = new Map<string, boolean>();
  for (const r of rows) {
    if (!inPageScope(scope, r.source_slug)) continue;
    let ok = reachableCache.get(r.target_wiki);
    if (ok === undefined) {
      const entry = await findEntry({ name: r.target_wiki });
      ok = entry !== null && existsSync(join(entry.path, ".almanac"));
      reachableCache.set(r.target_wiki, ok);
    }
    if (!ok) {
      out.push({
        source_slug: r.source_slug,
        target_wiki: r.target_wiki,
        target_slug: r.target_slug,
      });
    }
  }
  return out;
}
