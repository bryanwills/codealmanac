import { withFreshViewerDb } from "./db.js";
import { getViewerOverview } from "./overview.js";
import { getViewerPage } from "./page.js";
import {
  getViewerFileMentions,
  searchViewerPages,
  suggestViewerPages,
} from "./search.js";
import { getViewerTopic } from "./topic.js";
import {
  getViewerJobDetail,
  getViewerJobs,
} from "./jobs-api.js";
import { getViewerReview } from "./review-api.js";
import type { ViewerApi, ViewerApiContext } from "./types.js";

export type { ViewerReview } from "./review-api.js";
export type { ViewerApi, ViewerApiContext };

export function createViewerApi(ctx: ViewerApiContext): ViewerApi {
  return {
    async overview() {
      return getViewerOverview(ctx.repoRoot);
    },

    async page(slug) {
      return getViewerPage(ctx.repoRoot, slug);
    },

    async topic(slug) {
      return getViewerTopic(ctx.repoRoot, slug);
    },

    async search(query) {
      return searchViewerPages(ctx.repoRoot, query);
    },

    async suggest(query) {
      return suggestViewerPages(ctx.repoRoot, query);
    },

    async file(path) {
      return getViewerFileMentions(ctx.repoRoot, path);
    },

    async review() {
      return getViewerReview(ctx.repoRoot);
    },

    async jobs() {
      return getViewerJobs(ctx.repoRoot, ctx.runtime);
    },

    async job(jobId) {
      return withFreshViewerDb(ctx.repoRoot, async (db) => {
        return getViewerJobDetail(ctx.repoRoot, jobId, db, ctx.runtime);
      });
    },
  };
}
