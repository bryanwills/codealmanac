import type { WikiReviewStatus } from "./review-types.js";

export function cleanReviewMarkdown(markdown: string | undefined): string | null {
  const input = markdown ?? "";
  if (input.trim().length === 0) return null;
  return input.replace(/\s+$/g, "");
}

export function reviewTimestamp(now?: Date): string {
  return (now ?? new Date()).toISOString();
}

export function isReviewStatusFilter(
  value: string,
): value is WikiReviewStatus | "all" {
  return (
    value === "open" ||
    value === "decided" ||
    value === "applied" ||
    value === "all"
  );
}
