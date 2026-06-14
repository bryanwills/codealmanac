import type Database from "better-sqlite3";

import { buildSearchSqlPlan } from "./search-plan.js";

export {
  buildQuotedPrefixFtsQuery,
  buildQuotedTermFtsQuery,
  buildTokenPrefixFtsQuery,
} from "./fts.js";
export {
  buildFileMentionFilter,
  escapeGlobMeta,
  parentFolderPrefixes,
  type FileMentionFilter,
} from "./file-mentions.js";

export interface SearchPageOptions {
  query?: string;
  topics: string[];
  mentions?: string;
  since?: string;
  stale?: string;
  orphan?: boolean;
  includeArchive?: boolean;
  archived?: boolean;
}

export interface SearchPageResult {
  slug: string;
  title: string | null;
  description: string | null;
  updated_at: number;
  archived_at: number | null;
  superseded_by: string | null;
  topics: string[];
}

export function searchPages(
  db: Database.Database,
  options: SearchPageOptions,
): SearchPageResult[] {
  const { sql, params } = buildSearchSqlPlan(options);
  const rows = db.prepare<unknown[], PageRow>(sql).all(...params);
  const topicStmt = db.prepare<[string], { topic_slug: string }>(
    "SELECT topic_slug FROM page_topics WHERE page_slug = ? ORDER BY topic_slug",
  );
  return rows.map((row) => ({
    slug: row.slug,
    title: row.title,
    description: row.description,
    updated_at: row.updated_at,
    archived_at: row.archived_at,
    superseded_by: row.superseded_by,
    topics: topicStmt.all(row.slug).map((t) => t.topic_slug),
  }));
}

interface PageRow {
  slug: string;
  title: string | null;
  description: string | null;
  updated_at: number;
  archived_at: number | null;
  superseded_by: string | null;
}
