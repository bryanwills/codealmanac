import { join } from "node:path";

import { ensureFreshIndex } from "../../wiki/indexer/index.js";
import { resolveWikiRoot } from "../../wiki/indexer/resolve-wiki.js";
import { openIndex } from "../../wiki/indexer/schema.js";
import * as query from "../../wiki/query/index.js";

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

export type WikiSearchResult = query.search.SearchPageResult;

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
    return query.search.searchPages(db, request);
  } finally {
    db.close();
  }
}
