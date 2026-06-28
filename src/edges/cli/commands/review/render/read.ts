import type {
  GetWikiReviewItemResult,
  ListWikiReviewItemsResult,
  WikiReviewItem,
} from "../../../../../services/wiki/review-types.js";

import {
  renderReviewInvalidStatus,
  renderReviewMissingItem,
} from "./errors.js";
import { renderReviewItem } from "./item.js";
import { ok } from "./output.js";
import type { ReviewCommandOutput } from "./types.js";

export function renderReviewListResult(
  result: ListWikiReviewItemsResult,
  json?: boolean,
): ReviewCommandOutput {
  switch (result.status) {
    case "listed":
      return renderReviewList(result.items, json);
    case "invalid-status":
      return renderReviewInvalidStatus(json);
  }
}

export function renderReviewShowResult(
  result: GetWikiReviewItemResult,
  json?: boolean,
): ReviewCommandOutput {
  switch (result.status) {
    case "found":
      return renderReviewShow(result.item, json);
    case "missing":
      return renderReviewMissingItem(result.id);
  }
}

function renderReviewList(
  items: WikiReviewItem[],
  json?: boolean,
): ReviewCommandOutput {
  if (json === true) return ok(`${JSON.stringify(items, null, 2)}\n`);
  if (items.length === 0) return ok("");

  return ok(
    items
      .map((item) => `${item.status.padEnd(7)} ${item.id}  ${item.summary}`)
      .join("\n") + "\n",
  );
}

function renderReviewShow(
  item: WikiReviewItem,
  json?: boolean,
): ReviewCommandOutput {
  if (json === true) return ok(`${JSON.stringify(item, null, 2)}\n`);
  return ok(renderReviewItem(item));
}
