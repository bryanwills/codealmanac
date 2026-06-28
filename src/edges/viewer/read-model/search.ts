import * as wikiQuery from "../../../stores/wiki/query/index.js";
import { withFreshViewerDb } from "./db.js";
import type { ViewerPageSummary } from "./types.js";

export async function searchViewerPages(
  repoRoot: string,
  query: string,
): Promise<{ query: string; pages: ViewerPageSummary[] }> {
  return withFreshViewerDb(repoRoot, (db) => {
    return wikiQuery.pages.searchPages(db, { query, limit: 50 });
  });
}

export async function suggestViewerPages(
  repoRoot: string,
  query: string,
): Promise<{ query: string; pages: ViewerPageSummary[] }> {
  return withFreshViewerDb(repoRoot, (db) => {
    const trimmed = query.trim();
    if (trimmed.length === 0) return { query: trimmed, pages: [] };
    return wikiQuery.pages.searchPages(db, {
      query: trimmed,
      limit: 8,
      prefix: true,
    });
  });
}

export async function getViewerFileMentions(
  repoRoot: string,
  path: string,
): Promise<{ path: string; pages: ViewerPageSummary[] }> {
  return withFreshViewerDb(repoRoot, (db) => {
    return wikiQuery.pages.pagesMentioningPath(db, path);
  });
}
