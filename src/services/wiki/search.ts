import { join } from "node:path";

import { ensureFreshIndex } from "../../stores/wiki/indexer/index.js";
import { resolveWikiRoot } from "../../stores/wiki/indexer/resolve-wiki.js";
import { openIndex } from "../../stores/wiki/indexer/schema.js";
import * as query from "../../stores/wiki/query/index.js";

export interface SearchWikiPagesRequest {
  cwd: string;
  query?: string;
  topics: string[];
  mentions?: string;
  since?: string;
  stale?: string;
  orphan?: boolean;
  includeArchive?: boolean;
  archived?: boolean;
  wiki?: string;
}

export interface WikiSearchResult {
  slug: string;
  title: string | null;
  summary: string | null;
  updated_at: number;
  archived_at: number | null;
  superseded_by: string | null;
  topics: string[];
}

export async function searchWikiPages(
  request: SearchWikiPagesRequest,
): Promise<WikiSearchResult[]> {
  const repoRoot = await resolveWikiRoot({
    cwd: request.cwd,
    wiki: request.wiki,
  });
  await ensureFreshIndex({ repoRoot });

  const db = openIndex(join(repoRoot, ".almanac", "index.db"));
  try {
    return query.search.searchPages(db, request).map(searchResultFromQuery);
  } finally {
    db.close();
  }
}

function searchResultFromQuery(
  result: query.search.SearchPageResult,
): WikiSearchResult {
  return {
    slug: result.slug,
    title: result.title,
    summary: result.summary,
    updated_at: result.updated_at,
    archived_at: result.archived_at,
    superseded_by: result.superseded_by,
    topics: result.topics,
  };
}
