import { renderOutcome } from "../../outcome.js";
import type { WikiReviewStatus } from "../../../../../services/wiki/review-types.js";

import type { ReviewCommandOutput } from "./types.js";

export function renderReviewMissingMarkdown(
  commandName: string,
): ReviewCommandOutput {
  return renderReviewError(
    `${commandName} requires markdown text or piped stdin`,
  );
}

export function renderReviewInvalidStatus(
  json?: boolean,
): ReviewCommandOutput {
  return renderReviewError(
    "review list --status must be open, decided, applied, or all",
    json,
  );
}

export function renderReviewMissingItem(
  id: string,
  json?: boolean,
): ReviewCommandOutput {
  return renderReviewError(`no review item "${id}"`, json);
}

export function renderReviewAlreadyApplied(
  id: string,
  json?: boolean,
): ReviewCommandOutput {
  return renderReviewError(
    `review decide cannot change an applied item; reopen ${id} first`,
    json,
  );
}

export function renderReviewNotDecided(
  id: string,
  currentStatus: WikiReviewStatus,
  json?: boolean,
): ReviewCommandOutput {
  return renderReviewError(
    `review apply requires a decided item (${id} is ${currentStatus})`,
    json,
  );
}

function renderReviewError(
  message: string,
  json?: boolean,
): ReviewCommandOutput {
  return renderOutcome({ type: "error", message }, { json });
}
