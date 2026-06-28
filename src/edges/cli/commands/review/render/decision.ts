import type {
  ApplyWikiReviewItemResult,
  DecideWikiReviewItemResult,
  ReopenWikiReviewItemResult,
  WikiReviewItem,
} from "../../../../../services/wiki/review-types.js";

import {
  renderReviewAlreadyApplied,
  renderReviewMissingItem,
  renderReviewMissingMarkdown,
  renderReviewNotDecided,
} from "./errors.js";
import { ok } from "./output.js";
import type { ReviewCommandOutput } from "./types.js";

export function renderReviewDecideResult(
  result: DecideWikiReviewItemResult,
  json?: boolean,
): ReviewCommandOutput {
  switch (result.status) {
    case "decided":
      return renderReviewDecided(result.item);
    case "missing-markdown":
      return renderReviewMissingMarkdown("review decide");
    case "missing":
      return renderReviewMissingItem(result.id);
    case "already-applied":
      return renderReviewAlreadyApplied(result.id, json);
  }
}

export function renderReviewApplyResult(
  result: ApplyWikiReviewItemResult,
  json?: boolean,
): ReviewCommandOutput {
  switch (result.status) {
    case "applied":
      return renderReviewApplied(result.item);
    case "missing-markdown":
      return renderReviewMissingMarkdown("review apply");
    case "missing":
      return renderReviewMissingItem(result.id);
    case "not-decided":
      return renderReviewNotDecided(result.id, result.currentStatus, json);
  }
}

export function renderReviewReopenResult(
  result: ReopenWikiReviewItemResult,
): ReviewCommandOutput {
  switch (result.status) {
    case "reopened":
      return renderReviewReopened(result.item);
    case "missing":
      return renderReviewMissingItem(result.id);
  }
}

function renderReviewDecided(item: WikiReviewItem): ReviewCommandOutput {
  return ok(`decided review item: ${item.id}\n`);
}

function renderReviewApplied(item: WikiReviewItem): ReviewCommandOutput {
  return ok(`applied review item: ${item.id}\n`);
}

function renderReviewReopened(item: WikiReviewItem): ReviewCommandOutput {
  return ok(`reopened review item: ${item.id}\n`);
}
