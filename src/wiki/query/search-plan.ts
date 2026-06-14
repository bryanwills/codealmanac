import { parseDuration } from "../indexer/duration.js";
import { buildTokenPrefixFtsQuery } from "./fts.js";
import { appendFileMentionClause } from "./file-mentions.js";

export interface SearchPlanOptions {
  query?: string;
  topics: string[];
  mentions?: string;
  since?: string;
  stale?: string;
  orphan?: boolean;
}

export interface SearchSqlPlan {
  sql: string;
  params: (string | number)[];
}

export function buildSearchSqlPlan(options: SearchPlanOptions): SearchSqlPlan {
  const whereClauses: string[] = [];
  const params: (string | number)[] = [];

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

  if (options.query !== undefined && options.query.trim().length > 0) {
    return buildFtsSearchSqlPlan(options.query, whereClauses, params);
  }
  return {
    sql: buildListSearchSql(whereClauses),
    params,
  };
}

function buildFtsSearchSqlPlan(
  query: string,
  whereClauses: string[],
  params: (string | number)[],
): SearchSqlPlan {
  return {
    sql: `
      SELECT p.slug, p.title, p.description, p.updated_at
      FROM pages p
      JOIN fts_pages f ON f.slug = p.slug
      WHERE fts_pages MATCH ?
        ${whereClauses.length > 0 ? `AND ${whereClauses.join(" AND ")}` : ""}
      ORDER BY f.rank ASC, p.updated_at DESC, p.slug ASC
    `,
    params: [buildTokenPrefixFtsQuery(query), ...params],
  };
}

function buildListSearchSql(whereClauses: string[]): string {
  const where =
    whereClauses.length > 0 ? `WHERE ${whereClauses.join(" AND ")}` : "";
  return `
    SELECT p.slug, p.title, p.description, p.updated_at
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
