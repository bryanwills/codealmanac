import type {
  AddWikiReviewItemResult,
  WikiReviewItem,
} from "../../../../../services/wiki/review-types.js";

import { renderReviewMissingMarkdown } from "./errors.js";
import { ok } from "./output.js";
import type { ReviewCommandOutput } from "./types.js";

export function renderReviewAddResult(
  result: AddWikiReviewItemResult,
  json?: boolean,
): ReviewCommandOutput {
  switch (result.status) {
    case "added":
      return renderReviewAdded(result.item, json);
    case "missing-markdown":
      return renderReviewMissingMarkdown("review add");
  }
}

function renderReviewAdded(
  item: WikiReviewItem,
  json?: boolean,
): ReviewCommandOutput {
  if (json === true) return ok(`${JSON.stringify(item, null, 2)}\n`);
  return ok(`added review item: ${item.id}\n`);
}
