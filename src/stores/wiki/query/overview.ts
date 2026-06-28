import type Database from "better-sqlite3";

export interface WikiOverviewCounts {
  pageCount: number;
  topicCount: number;
}

export function wikiOverviewCounts(db: Database.Database): WikiOverviewCounts {
  const row = db
    .prepare<[], { page_count: number; topic_count: number }>(
      `SELECT
         (SELECT COUNT(*) FROM pages WHERE archived_at IS NULL) AS page_count,
         (SELECT COUNT(*) FROM topics) AS topic_count`,
    )
    .get() ?? { page_count: 0, topic_count: 0 };

  return {
    pageCount: row.page_count,
    topicCount: row.topic_count,
  };
}
