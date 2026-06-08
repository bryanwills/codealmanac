import type Database from "better-sqlite3";

import { parseDuration } from "../indexer/duration.js";
import { looksLikeDir, normalizePath } from "../indexer/paths.js";

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
  summary: string | null;
  updated_at: number;
  archived_at: number | null;
  superseded_by: string | null;
  topics: string[];
}

export interface FileMentionFilter {
  isDir: boolean;
  normalizedPath: string;
  globPrefix: string;
  parentFolders: string[];
}

/**
 * CLI text search: tokenize into alphanumeric runs and use FTS5 prefix tokens.
 */
export function buildTokenPrefixFtsQuery(raw: string): string {
  const trimmed = raw.trim();
  if (
    trimmed.length >= 2 &&
    trimmed.startsWith("\"") &&
    trimmed.endsWith("\"")
  ) {
    const inner = trimmed
      .slice(1, -1)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
    if (inner.length === 0) return "\"\"";
    return `"${inner}"`;
  }
  const tokens = trimmed
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length > 0);
  if (tokens.length === 0) return "\"\"";
  return tokens.map((t) => `${t}*`).join(" AND ");
}

/**
 * Viewer submitted search: quote whitespace terms for complete-query matching.
 */
export function buildQuotedTermFtsQuery(input: string): string {
  return input
    .split(/\s+/)
    .map((term) => term.replace(/"/g, ""))
    .filter((term) => term.length > 0)
    .map((term) => `"${term}"`)
    .join(" AND ");
}

/**
 * Viewer suggestions: quote terms but allow FTS5 prefix matching while typing.
 */
export function buildQuotedPrefixFtsQuery(input: string): string {
  return input
    .split(/\s+/)
    .map((term) => term.replace(/["*]/g, ""))
    .filter((term) => term.length > 0)
    .map((term) => `"${term}"*`)
    .join(" AND ");
}

export function buildFileMentionFilter(input: string): FileMentionFilter {
  const isDir = looksLikeDir(input);
  const normalizedPath = normalizePath(input, isDir);
  return {
    isDir,
    normalizedPath,
    globPrefix: `${escapeGlobMeta(normalizedPath)}*`,
    parentFolders: isDir ? [] : parentFolderPrefixes(normalizedPath),
  };
}

/**
 * For a normalized file path like `src/checkout/handler.ts`, enumerate
 * every containing folder in stored form: `['src/', 'src/checkout/']`.
 */
export function parentFolderPrefixes(filePath: string): string[] {
  const out: string[] = [];
  let cursor = 0;
  while (true) {
    const next = filePath.indexOf("/", cursor);
    if (next === -1) break;
    out.push(filePath.slice(0, next + 1));
    cursor = next + 1;
  }
  return out;
}

export function escapeGlobMeta(input: string): string {
  return input.replace(/[\*\?\[]/g, (ch) => `[${ch}]`);
}

export function searchPages(
  db: Database.Database,
  options: SearchPageOptions,
): SearchPageResult[] {
  const whereClauses: string[] = [];
  const params: (string | number)[] = [];

  if (options.archived === true) {
    whereClauses.push("p.archived_at IS NOT NULL");
  } else if (options.includeArchive !== true) {
    whereClauses.push("p.archived_at IS NULL");
  }

  for (const rawTopic of options.topics) {
    const topicSlug = slugForTopic(rawTopic);
    if (topicSlug.length === 0) continue;
    whereClauses.push(
      "EXISTS (SELECT 1 FROM page_topics pt WHERE pt.page_slug = p.slug AND pt.topic_slug = ?)",
    );
    params.push(topicSlug);
  }

  if (options.mentions !== undefined && options.mentions.length > 0) {
    appendFileMentionClause(whereClauses, params, options.mentions);
  }

  const now = Math.floor(Date.now() / 1000);

  if (options.since !== undefined) {
    const seconds = parseDuration(options.since);
    whereClauses.push("p.updated_at >= ?");
    params.push(now - seconds);
  }

  if (options.stale !== undefined) {
    const seconds = parseDuration(options.stale);
    whereClauses.push("p.updated_at < ?");
    params.push(now - seconds);
  }

  if (options.orphan === true) {
    whereClauses.push(
      "NOT EXISTS (SELECT 1 FROM page_topics pt WHERE pt.page_slug = p.slug)",
    );
  }

  let sql: string;
  if (options.query !== undefined && options.query.trim().length > 0) {
    const ftsExpr = buildTokenPrefixFtsQuery(options.query);
    sql = `
      SELECT p.slug, p.title, p.summary, p.updated_at, p.archived_at, p.superseded_by
      FROM pages p
      JOIN fts_pages f ON f.slug = p.slug
      WHERE fts_pages MATCH ?
        ${whereClauses.length > 0 ? `AND ${whereClauses.join(" AND ")}` : ""}
      ORDER BY f.rank ASC, p.updated_at DESC, p.slug ASC
    `;
    params.unshift(ftsExpr);
  } else {
    sql = buildSearchSql(whereClauses);
  }

  const rows = db.prepare<unknown[], PageRow>(sql).all(...params);
  const topicStmt = db.prepare<[string], { topic_slug: string }>(
    "SELECT topic_slug FROM page_topics WHERE page_slug = ? ORDER BY topic_slug",
  );
  return rows.map((row) => ({
    slug: row.slug,
    title: row.title,
    summary: row.summary,
    updated_at: row.updated_at,
    archived_at: row.archived_at,
    superseded_by: row.superseded_by,
    topics: topicStmt.all(row.slug).map((t) => t.topic_slug),
  }));
}

interface PageRow {
  slug: string;
  title: string | null;
  summary: string | null;
  updated_at: number;
  archived_at: number | null;
  superseded_by: string | null;
}

function appendFileMentionClause(
  whereClauses: string[],
  params: (string | number)[],
  input: string,
): void {
  const mention = buildFileMentionFilter(input);
  if (mention.isDir) {
    // Folder queries need GLOB for prefix matching, but the pattern is
    // built from the user query after escaping GLOB metacharacters.
    // Never concatenate stored file_refs paths into a GLOB pattern:
    // Next.js-style paths such as `src/[id]/page.tsx` must stay literal.
    whereClauses.push(
      `EXISTS (
         SELECT 1 FROM file_refs r
         WHERE r.page_slug = p.slug
           AND (r.path = ? OR r.path GLOB ?)
       )`,
    );
    params.push(mention.normalizedPath, mention.globPrefix);
    return;
  }

  // File queries match the exact file plus any containing folder refs.
  // Use equality over enumerated parent folders instead of GLOB over
  // stored values so metacharacters in stored paths remain literal.
  if (mention.parentFolders.length === 0) {
    whereClauses.push(
      `EXISTS (
         SELECT 1 FROM file_refs r
         WHERE r.page_slug = p.slug AND r.path = ?
       )`,
    );
    params.push(mention.normalizedPath);
    return;
  }

  const placeholders = mention.parentFolders.map(() => "?").join(", ");
  whereClauses.push(
    `EXISTS (
       SELECT 1 FROM file_refs r
       WHERE r.page_slug = p.slug
         AND (
           r.path = ?
           OR (r.is_dir = 1 AND r.path IN (${placeholders}))
         )
     )`,
  );
  params.push(mention.normalizedPath, ...mention.parentFolders);
}

function buildSearchSql(whereClauses: string[]): string {
  const where =
    whereClauses.length > 0 ? `WHERE ${whereClauses.join(" AND ")}` : "";
  return `
    SELECT p.slug, p.title, p.summary, p.updated_at, p.archived_at, p.superseded_by
    FROM pages p
    ${where}
    ORDER BY p.updated_at DESC, p.slug ASC
  `;
}

function slugForTopic(raw: string): string {
  return raw
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
