import { join } from "node:path";

import { ensureFreshIndex } from "../../stores/wiki/indexer/index.js";
import { resolveWikiRoot } from "../../stores/wiki/indexer/resolve-wiki.js";
import { openIndex } from "../../stores/wiki/indexer/schema.js";
import * as query from "../../stores/wiki/query/index.js";

export interface WikiPageFileRef {
  path: string;
  is_dir: boolean;
}

export interface WikiPageSource {
  id: string;
  type: string;
  target: string;
  title: string | null;
  retrieved_at: string | null;
  note: string | null;
  legacy: boolean;
}

export interface WikiCrossWikiLink {
  wiki: string;
  target: string;
}

export interface WikiPageView {
  slug: string;
  title: string | null;
  summary: string | null;
  file_path: string;
  updated_at: number;
  archived_at: number | null;
  superseded_by: string | null;
  supersedes: string[];
  topics: string[];
  file_refs: WikiPageFileRef[];
  sources: WikiPageSource[];
  wikilinks_out: string[];
  wikilinks_in: string[];
  cross_wiki_links: WikiCrossWikiLink[];
  body: string;
}

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
        records.push(pageViewFromQuery(record));
      }
    }
    return { records, missing };
  } finally {
    db.close();
  }
}

function pageViewFromQuery(record: query.PageView): WikiPageView {
  return {
    slug: record.slug,
    title: record.title,
    summary: record.summary,
    file_path: record.file_path,
    updated_at: record.updated_at,
    archived_at: record.archived_at,
    superseded_by: record.superseded_by,
    supersedes: record.supersedes,
    topics: record.topics,
    file_refs: record.file_refs,
    sources: record.sources,
    wikilinks_out: record.wikilinks_out,
    wikilinks_in: record.wikilinks_in,
    cross_wiki_links: record.cross_wiki_links,
    body: record.body,
  };
}
