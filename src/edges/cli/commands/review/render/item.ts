import type { WikiReviewItem } from "../../../../../services/wiki/review-types.js";

export function renderReviewItem(item: WikiReviewItem): string {
  const lines = [
    `id: ${item.id}`,
    `status: ${item.status}`,
    `summary: ${item.summary}`,
    `created: ${item.created_at}`,
  ];
  if (item.decided_at !== null) lines.push(`decided: ${item.decided_at}`);
  if (item.applied_at !== null) lines.push(`applied: ${item.applied_at}`);
  if (item.reopened_at !== undefined && item.reopened_at !== null) {
    lines.push(`reopened: ${item.reopened_at}`);
  }
  lines.push("", item.body.trimEnd(), "");
  if (item.decision !== null) {
    lines.push("Decision:", item.decision.trimEnd(), "");
  }
  if (item.application !== null) {
    lines.push("Application:", item.application.trimEnd(), "");
  }
  if (
    item.reopen_note !== undefined &&
    item.reopen_note !== null &&
    item.reopen_note.length > 0
  ) {
    lines.push("Reopen note:", item.reopen_note.trimEnd(), "");
  }
  return lines.join("\n");
}
