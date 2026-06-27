import type {
  ReviewItem,
  ReviewStatus,
} from "../../stores/wiki-review/store.js";

export type { ReviewItem, ReviewStatus } from "../../stores/wiki-review/store.js";

export interface WikiReviewRequest {
  cwd: string;
  wiki?: string;
}

export interface AddWikiReviewItemRequest extends WikiReviewRequest {
  markdown?: string;
  now?: Date;
}

export interface ListWikiReviewItemsRequest extends WikiReviewRequest {
  status?: ReviewStatus | "all" | string;
}

export interface WikiReviewItemRequest extends WikiReviewRequest {
  id: string;
}

export interface ChangeWikiReviewItemRequest extends WikiReviewItemRequest {
  markdown?: string;
  now?: Date;
}

export type AddWikiReviewItemResult =
  | { status: "added"; item: ReviewItem }
  | { status: "missing-markdown" };

export type ListWikiReviewItemsResult =
  | { status: "listed"; items: ReviewItem[] }
  | { status: "invalid-status" };

export type GetWikiReviewItemResult =
  | { status: "found"; item: ReviewItem }
  | { status: "missing"; id: string };

export type DecideWikiReviewItemResult =
  | { status: "decided"; item: ReviewItem }
  | { status: "missing-markdown" }
  | { status: "missing"; id: string }
  | { status: "already-applied"; id: string };

export type ApplyWikiReviewItemResult =
  | { status: "applied"; item: ReviewItem }
  | { status: "missing-markdown" }
  | { status: "missing"; id: string }
  | { status: "not-decided"; id: string; currentStatus: ReviewStatus };

export type ReopenWikiReviewItemResult =
  | { status: "reopened"; item: ReviewItem }
  | { status: "missing"; id: string };
