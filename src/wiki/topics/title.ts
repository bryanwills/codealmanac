/**
 * Convert a topic slug back to a human-readable fallback title:
 * `auth-flow` -> `Auth Flow`.
 */
export function topicTitleFromSlug(slug: string): string {
  if (slug.length === 0) return slug;
  return slug
    .split("-")
    .filter((part) => part.length > 0)
    .map((part) => `${part[0]?.toUpperCase() ?? ""}${part.slice(1)}`)
    .join(" ");
}
