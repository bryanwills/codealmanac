import * as wikiQuery from "../../../stores/wiki/query/index.js";
import { withFreshViewerDb } from "./db.js";
import type { ViewerTopic } from "./types.js";

export async function getViewerTopic(
  repoRoot: string,
  slug: string,
): Promise<ViewerTopic | null> {
  return withFreshViewerDb(repoRoot, (db) => {
    return wikiQuery.topics.topicDetail(db, slug);
  });
}
