import type Database from "better-sqlite3";

import { toKebabCase } from "../../slug.js";
import { topicTitleFromSlug } from "../topics/title.js";
import {
  looksLikeDir,
  normalizePath,
  normalizePathPreservingCase,
} from "./paths.js";
import type { IndexedPagesPlan } from "./page-plan.js";

export function applyIndexedPagesPlan(
  db: Database.Database,
  plan: IndexedPagesPlan,
): void {
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
      // FTS5 virtual tables do not receive FK cascades. Delete FTS rows
      // explicitly before page deletion so old content cannot remain
      // searchable for removed pages.
      deleteFtsByPage.run(slug);
      deleteByPage.run(slug);
    }

    for (const p of plan.planned) {
      deletePageProjectionRows(p.slug, {
        deletePageTopics,
        deleteFileRefs,
        deletePageSources,
        deleteWikilinks,
        deleteXwiki,
        deleteFtsByPage,
      });

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

      for (const ref of p.sourceFileRefs) {
        const raw = ref.rawPath;
        const isDir = looksLikeDir(raw);
        const path = normalizePath(raw, isDir);
        const originalPath = normalizePathPreservingCase(raw, isDir);
        if (path.length === 0) continue;
        insertFileRef.run(p.slug, path, originalPath, isDir ? 1 : 0);
      }

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
}

function deletePageProjectionRows(
  slug: string,
  statements: {
    deletePageTopics: Database.Statement<[string]>;
    deleteFileRefs: Database.Statement<[string]>;
    deletePageSources: Database.Statement<[string]>;
    deleteWikilinks: Database.Statement<[string]>;
    deleteXwiki: Database.Statement<[string]>;
    deleteFtsByPage: Database.Statement<[string]>;
  },
): void {
  statements.deletePageTopics.run(slug);
  statements.deleteFileRefs.run(slug);
  statements.deletePageSources.run(slug);
  statements.deleteWikilinks.run(slug);
  statements.deleteXwiki.run(slug);
  statements.deleteFtsByPage.run(slug);
}
