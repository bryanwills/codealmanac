import { toKebabCase } from "../../../shared/slug.js";
import * as wikiQuery from "../../../stores/wiki/query/index.js";
import { withFreshViewerDb } from "./db.js";
import type { ViewerPage } from "./types.js";

export async function getViewerPage(
  repoRoot: string,
  slug: string,
): Promise<ViewerPage | null> {
  return withFreshViewerDb(repoRoot, async (db) => {
    const page = await wikiQuery.getPageView(db, toKebabCase(slug));
    if (page === null) return null;
    const relatedSlugs = Array.from(new Set([
      ...page.wikilinks_in,
      ...page.wikilinks_out,
      ...page.supersedes,
      ...(page.superseded_by !== null ? [page.superseded_by] : []),
    ]));
    const related_pages = wikiQuery.pages.pagesBySlug(db, relatedSlugs);
    return { ...page, related_pages };
  });
}
