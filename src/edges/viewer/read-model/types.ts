import type * as wikiQuery from "../../../stores/wiki/query/index.js";
import type {
  ViewerJobDetail,
  ViewerJobRun,
  ViewerJobsRuntime,
} from "./jobs-api.js";
import type { ViewerReview } from "./review-api.js";

export interface ViewerApiContext {
  repoRoot: string;
  runtime: ViewerJobsRuntime;
}

export type ViewerPageSummary = wikiQuery.PageSummary;
export type ViewerTopicSummary = wikiQuery.TopicSummary;
export type ViewerTopic = wikiQuery.TopicDetail;
export type ViewerPage = wikiQuery.PageView & {
  related_pages: ViewerPageSummary[];
};

export interface ViewerOverview {
  repoRoot: string;
  wikiTitle: string;
  pageCount: number;
  topicCount: number;
  recentPages: ViewerPageSummary[];
  topics: ViewerTopicSummary[];
  rootTopics: ViewerTopicSummary[];
  topicNavigation: {
    source: "curated" | "tags";
    sidebarLimit: number;
  };
  featuredPages: {
    gettingStarted: ViewerPageSummary | null;
  };
}

export interface ViewerApi {
  overview(): Promise<ViewerOverview>;
  page(slug: string): Promise<ViewerPage | null>;
  topic(slug: string): Promise<ViewerTopic | null>;
  search(query: string): Promise<{ query: string; pages: ViewerPageSummary[] }>;
  suggest(query: string): Promise<{ query: string; pages: ViewerPageSummary[] }>;
  file(path: string): Promise<{ path: string; pages: ViewerPageSummary[] }>;
  review(): Promise<ViewerReview>;
  jobs(): Promise<{ runs: ViewerJobRun[] }>;
  job(jobId: string): Promise<ViewerJobDetail | null>;
}
