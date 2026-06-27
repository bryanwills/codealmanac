import { join } from "node:path";

import { ensureFreshIndex } from "../../wiki/indexer/index.js";
import { resolveWikiRoot } from "../../wiki/indexer/resolve-wiki.js";
import { openIndex } from "../../wiki/indexer/schema.js";
import * as query from "../../wiki/query/index.js";

export type WikiPageView = query.PageView;

export interface ReadWikiPagesRequest {
  cwd: string;
  wiki?: string;
  slugs: string[];
}

export interface ReadWikiPagesResult {
  records: WikiPageView[];
  missing: string[];
}

export async function readWikiPages(
  request: ReadWikiPagesRequest,
): Promise<ReadWikiPagesResult> {
  const repoRoot = await resolveWikiRoot({
    cwd: request.cwd,
    wiki: request.wiki,
  });
  await ensureFreshIndex({ repoRoot });

  const db = openIndex(join(repoRoot, ".almanac", "index.db"));
  try {
    const records: WikiPageView[] = [];
    const missing: string[] = [];
    for (const slug of request.slugs) {
      const record = await query.getPageView(db, slug);
      if (record === null) {
        missing.push(slug);
      } else {
        records.push(record);
      }
    }
    return { records, missing };
  } finally {
    db.close();
  }
}
