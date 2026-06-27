import type {
  ReviewItem as StoredReviewItem,
  ReviewStatus as StoredReviewStatus,
} from "../../stores/wiki-review/store.js";

export type WikiReviewItem = StoredReviewItem;
export type WikiReviewStatus = StoredReviewStatus;

export interface WikiReviewRequest {
  cwd: string;
  wiki?: string;
}

export interface AddWikiReviewItemRequest extends WikiReviewRequest {
  markdown?: string;
  now?: Date;
}

export interface ListWikiReviewItemsRequest extends WikiReviewRequest {
  status?: WikiReviewStatus | "all" | string;
}

export interface WikiReviewItemRequest extends WikiReviewRequest {
  id: string;
}

export interface ChangeWikiReviewItemRequest extends WikiReviewItemRequest {
  markdown?: string;
  now?: Date;
}

export type AddWikiReviewItemResult =
  | { status: "added"; item: WikiReviewItem }
  | { status: "missing-markdown" };

export type ListWikiReviewItemsResult =
  | { status: "listed"; items: WikiReviewItem[] }
  | { status: "invalid-status" };

export type GetWikiReviewItemResult =
  | { status: "found"; item: WikiReviewItem }
  | { status: "missing"; id: string };

export type DecideWikiReviewItemResult =
  | { status: "decided"; item: WikiReviewItem }
  | { status: "missing-markdown" }
  | { status: "missing"; id: string }
  | { status: "already-applied"; id: string };

export type ApplyWikiReviewItemResult =
  | { status: "applied"; item: WikiReviewItem }
  | { status: "missing-markdown" }
  | { status: "missing"; id: string }
  | { status: "not-decided"; id: string; currentStatus: WikiReviewStatus };

export type ReopenWikiReviewItemResult =
  | { status: "reopened"; item: WikiReviewItem }
  | { status: "missing"; id: string };
