import * as wikiQuery from "../../../stores/wiki/query/index.js";
import { hasTopicsFile } from "../../../stores/wiki/topics/yaml.js";
import { withFreshViewerDb } from "./db.js";
import type { ViewerOverview } from "./types.js";

const SIDEBAR_TAG_LIMIT = 8;

export async function getViewerOverview(repoRoot: string): Promise<ViewerOverview> {
  return withFreshViewerDb(repoRoot, (db) => {
    const counts = wikiQuery.overview.wikiOverviewCounts(db);
    const topicNavigation = {
      source: hasTopicsFile(repoRoot) ? "curated" as const : "tags" as const,
      sidebarLimit: SIDEBAR_TAG_LIMIT,
    };

    return {
      repoRoot,
      wikiTitle: "Almanac",
      pageCount: counts.pageCount,
      topicCount: counts.topicCount,
      recentPages: wikiQuery.pages.recentPages(db, 60),
      topics: wikiQuery.topics.topicSummaries(db, {
        rootsOnly: false,
        order: "page_count",
      }),
      rootTopics: wikiQuery.topics.topicSummaries(db, {
        rootsOnly: true,
        limit:
          topicNavigation.source === "curated"
            ? 24
            : topicNavigation.sidebarLimit,
        order: "page_count",
      }),
      topicNavigation,
      featuredPages: {
        gettingStarted: wikiQuery.pages.pageSummaryBySlug(db, "getting-started"),
      },
    };
  });
}
