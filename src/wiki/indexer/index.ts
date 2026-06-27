import { existsSync } from "node:fs";
import { utimes } from "node:fs/promises";
import { join } from "node:path";

import type Database from "better-sqlite3";

import { toKebabCase } from "../../slug.js";
import { topicTitleFromSlug } from "../topics/title.js";
import {
  pagesNewerThan,
  topicsYamlNewerThan,
} from "./freshness.js";
import {
  normalizePath,
  normalizePathPreservingCase,
  looksLikeDir,
} from "./paths.js";
import {
  buildIndexedPagesPlan,
  type ExistingIndexedPage,
} from "./page-plan.js";
import { isIndexSchemaStale, openIndex } from "./schema.js";
import { applyTopicsYaml, TOPICS_YAML_FILENAME } from "./topics-yaml.js";

export interface IndexContext {
  /** Absolute path to the repo root (the dir containing `.almanac/`). */
  repoRoot: string;
}

export interface IndexResult {
  /** Pages parsed or re-parsed during this run. Zero when the DB was already up to date. */
  changed: number;
  /** Pages present in the DB before this run but missing from disk. */
  removed: number;
  /**
   * Pages on disk at the end of this run — i.e. files that made it all the
   * way through to the index. Skipped files (slug collisions, unreadable,
   * un-sluggable filenames) are NOT counted here. Use `filesSeen` for the
   * raw count of `.md` files encountered on disk.
   *
   * Alias retained for backwards-compat with existing tests/consumers; new
   * code should prefer `pagesIndexed` for clarity.
   */
  total: number;
  /** Pages that made it into the index. Same number as `total`. */
  pagesIndexed: number;
  /**
   * Count of `.md` files found under `pages/` before any filtering. Always
   * `>= pagesIndexed`; the difference is `filesSkipped`.
   */
  filesSeen: number;
  /**
   * Files dropped before making it into the index — slug collisions,
   * un-sluggable filenames, or filesystem races (deleted/unreadable mid-run).
   * Covered by stderr warnings when non-zero.
   */
  filesSkipped: number;
}

/**
 * The "front door" for query commands. Runs the indexer only if the DB is
 * missing or at least one page is newer than it. Meant to be cheap — the
 * common case is "nothing changed, mtime check returns fast, we're done".
 *
 * The spec is explicit: "Reindex is implicit and invisible. If the user
 * didn't didn't explicitly run `reindex`, they shouldn't see reindex
 * output. Silent by default." So this function never writes to stdout;
 * warnings (slug collisions, bad frontmatter) still go to stderr.
 */
export async function ensureFreshIndex(ctx: IndexContext): Promise<IndexResult> {
  const almanacDir = join(ctx.repoRoot, ".almanac");
  const dbPath = join(almanacDir, "index.db");
  const pagesDir = join(almanacDir, "pages");

  if (!existsSync(pagesDir)) {
    // No pages dir = nothing to index. Open/create the DB so downstream
    // queries can run against an empty schema rather than crashing on a
    // missing file.
    const db = openIndex(dbPath);
    db.close();
    return emptyResult();
  }

  if (indexNeedsRefresh({ almanacDir, dbPath, pagesDir })) {
    return runIndexer(ctx);
  }
  return emptyResult();
}

function indexNeedsRefresh(args: {
  almanacDir: string;
  dbPath: string;
  pagesDir: string;
}): boolean {
  if (!existsSync(args.dbPath)) return true;
  if (isIndexSchemaStale(args.dbPath)) return true;

  // Keep read-side freshness even when CLI/agent write paths eagerly
  // reindex: users can still change `.almanac/pages/` directly via
  // manual edits, git pulls, merges, or branch switches.
  return (
    pagesNewerThan(args.pagesDir, args.dbPath) ||
    topicsYamlNewerThan(args.almanacDir, args.dbPath)
  );
}

function emptyResult(): IndexResult {
  return {
    changed: 0,
    removed: 0,
    total: 0,
    pagesIndexed: 0,
    filesSeen: 0,
    filesSkipped: 0,
  };
}

/**
 * Force a full reindex. Identical to `ensureFreshIndex` except it runs
 * the indexer unconditionally. Exposed for `almanac reindex`.
 */
export async function runIndexer(ctx: IndexContext): Promise<IndexResult> {
  const almanacDir = join(ctx.repoRoot, ".almanac");
  const dbPath = join(almanacDir, "index.db");
  const pagesDir = join(almanacDir, "pages");

  const db = openIndex(dbPath);
  let result: IndexResult;
  try {
    result = await indexPagesInto(db, pagesDir);
    // After pages are indexed, reconcile the topics table against
    // `.almanac/topics.yaml` (if present). `indexPagesInto` has already
    // lazily inserted rows for every topic slug mentioned in page
    // frontmatter with a title-cased title; `applyTopicsYaml` now
    // promotes the declared title/description and rewrites parent edges
    // for those topics that live in the file.
    await applyTopicsYaml(db, join(almanacDir, TOPICS_YAML_FILENAME));
  } finally {
    db.close();
  }

  // Bump the DB mtime to "now" after a successful reindex (even a no-op
  // one). Otherwise, a page file with a future mtime (clock skew,
  // `git checkout` preserving source mtimes) would trigger `ensureFreshIndex`
  // on every query: the freshness check sees `page.mtime > db.mtime`,
  // reindex runs, finds no content-hash changes, and the DB mtime stays
  // stale — locking us into a reindex-on-every-query loop. Touching the
  // DB mtime makes the comparison monotonic.
  try {
    const now = new Date();
    await utimes(dbPath, now, now);
  } catch {
    // Touching mtime is a freshness optimization; failures here are
    // non-fatal and the reindex result is still correct.
  }
  return result;
}

async function indexPagesInto(
  db: Database.Database,
  pagesDir: string,
): Promise<IndexResult> {
  // Load the current state of the index into memory so we can diff against
  // what's on disk. This is cheap even at 10k pages (one INTEGER + two
  // short strings per row).
  const existingRows = db
    .prepare<[], ExistingIndexedPage>(
      "SELECT slug, content_hash, file_path FROM pages",
    )
    .all();
  const plan = await buildIndexedPagesPlan({ pagesDir, existingRows });

  const deleteByPage = db.prepare<[string]>("DELETE FROM pages WHERE slug = ?");
  const deleteFtsByPage = db.prepare<[string]>(
    "DELETE FROM fts_pages WHERE slug = ?",
  );

  const replacePage = db.prepare<
    [string, string, string | null, string, string, number, number | null, string | null]
  >(
    `INSERT INTO pages (slug, title, summary, file_path, content_hash, updated_at, archived_at, superseded_by)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(slug) DO UPDATE SET
       title         = excluded.title,
       summary       = excluded.summary,
       file_path     = excluded.file_path,
       content_hash  = excluded.content_hash,
       updated_at    = excluded.updated_at,
       archived_at   = excluded.archived_at,
       superseded_by = excluded.superseded_by`,
  );

  const deletePageTopics = db.prepare<[string]>(
    "DELETE FROM page_topics WHERE page_slug = ?",
  );
  const insertPageTopic = db.prepare<[string, string]>(
    "INSERT OR IGNORE INTO page_topics (page_slug, topic_slug) VALUES (?, ?)",
  );
  // Seed ad-hoc topics with a title-cased default. If the topic is
  // later declared in `.almanac/topics.yaml`, `applyTopicsYaml` will
  // promote the title/description to whatever the file says. We set the
  // title here (rather than leaving NULL) so `topics list` and
  // `health --topic` have a display name even before a user writes to
  // topics.yaml.
  const insertTopic = db.prepare<[string, string]>(
    "INSERT OR IGNORE INTO topics (slug, title) VALUES (?, ?)",
  );

  const deleteFileRefs = db.prepare<[string]>(
    "DELETE FROM file_refs WHERE page_slug = ?",
  );
  const insertFileRef = db.prepare<[string, string, string, number]>(
    "INSERT OR IGNORE INTO file_refs (page_slug, path, original_path, is_dir) VALUES (?, ?, ?, ?)",
  );

  const deletePageSources = db.prepare<[string]>(
    "DELETE FROM page_sources WHERE page_slug = ?",
  );
  const insertPageSource = db.prepare<
    [string, string, string, string, string | null, string | null, string | null, number]
  >(
    `INSERT OR IGNORE INTO page_sources
       (page_slug, source_id, source_type, target, title, retrieved_at, note, legacy)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
  );

  const deleteWikilinks = db.prepare<[string]>(
    "DELETE FROM wikilinks WHERE source_slug = ?",
  );
  const insertWikilink = db.prepare<[string, string]>(
    "INSERT OR IGNORE INTO wikilinks (source_slug, target_slug) VALUES (?, ?)",
  );

  const deleteXwiki = db.prepare<[string]>(
    "DELETE FROM cross_wiki_links WHERE source_slug = ?",
  );
  const insertXwiki = db.prepare<[string, string, string]>(
    "INSERT OR IGNORE INTO cross_wiki_links (source_slug, target_wiki, target_slug) VALUES (?, ?, ?)",
  );

  const insertFts = db.prepare<[string, string, string]>(
    "INSERT INTO fts_pages (slug, title, content) VALUES (?, ?, ?)",
  );

  const apply = db.transaction(() => {
    for (const slug of plan.toDelete) {
      // `fts_pages` is an FTS5 virtual table — FK cascades do NOT propagate
      // into it, so we must delete FTS rows explicitly before relying on
      // `DELETE FROM pages` to cascade-clean the four real tables
      // (page_topics, file_refs, wikilinks, cross_wiki_links). If this
      // explicit delete ever gets removed, orphaned FTS rows will show up
      // as phantom search hits pointing at non-existent slugs.
      deleteFtsByPage.run(slug);
      deleteByPage.run(slug); // CASCADE cleans page_topics, file_refs, wikilinks, cross_wiki_links
    }

    for (const p of plan.planned) {
      // page_topics/file_refs/wikilinks/cross_wiki_links all cascade on
      // delete, so the cleanest "replace" story is: delete-then-insert
      // the per-page rows under the same transaction. Doing it this way
      // (rather than `ON CONFLICT DO UPDATE` per row) keeps the logic
      // uniform and makes "remove a topic from frontmatter" work.
      deletePageTopics.run(p.slug);
      deleteFileRefs.run(p.slug);
      deletePageSources.run(p.slug);
      deleteWikilinks.run(p.slug);
      deleteXwiki.run(p.slug);
      // Same virtual-table reason as the deletion branch above — FTS5
      // rows do not cascade, so clean them by hand before reinserting.
      deleteFtsByPage.run(p.slug);

      replacePage.run(
        p.slug,
        p.title,
        p.summary ?? null,
        p.fullPath,
        p.contentHash,
        p.updatedAt,
        p.archivedAt,
        p.supersededBy,
      );

      for (const topic of p.topics) {
        const topicSlug = toKebabCase(topic);
        if (topicSlug.length === 0) continue;
        insertTopic.run(topicSlug, topicTitleFromSlug(topicSlug));
        insertPageTopic.run(p.slug, topicSlug);
      }

      for (const source of p.pageSources) {
        const sourceTarget = source.type === "file"
          ? normalizePath(source.target, looksLikeDir(source.target))
          : source.target;
        insertPageSource.run(
          p.slug,
          source.id,
          source.type,
          sourceTarget,
          source.title ?? null,
          source.retrieved_at ?? null,
          source.note ?? null,
          source.legacy ? 1 : 0,
        );
      }

      // Source-derived file references. `src/wiki/indexer/page-sources.ts`
      // is the only place that knows legacy `files:` can still become
      // file refs; the indexer consumes the normalized model.
      for (const ref of p.sourceFileRefs) {
        const raw = ref.rawPath;
        const isDir = looksLikeDir(raw);
        const path = normalizePath(raw, isDir);
        const originalPath = normalizePathPreservingCase(raw, isDir);
        if (path.length === 0) continue;
        insertFileRef.run(p.slug, path, originalPath, isDir ? 1 : 0);
      }

      // Inline `[[...]]` extracted from body.
      for (const ref of p.wikilinks) {
        switch (ref.kind) {
          case "page":
            insertWikilink.run(p.slug, ref.target);
            break;
          case "file":
            insertFileRef.run(p.slug, ref.path, ref.originalPath, 0);
            break;
          case "folder":
            insertFileRef.run(p.slug, ref.path, ref.originalPath, 1);
            break;
          case "xwiki":
            insertXwiki.run(p.slug, ref.wiki, ref.target);
            break;
        }
      }

      insertFts.run(
        p.slug,
        p.title,
        [p.summary, p.content].filter((part) => part !== undefined).join("\n\n"),
      );
    }
  });
  apply();

  return {
    changed: plan.planned.length,
    removed: plan.toDelete.length,
    total: plan.pagesIndexed,
    pagesIndexed: plan.pagesIndexed,
    filesSeen: plan.filesSeen,
    filesSkipped: plan.filesSkipped,
  };
}
