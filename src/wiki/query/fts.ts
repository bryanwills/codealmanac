/**
 * CLI text search: tokenize into alphanumeric runs and use FTS5 prefix tokens.
 */
export function buildTokenPrefixFtsQuery(raw: string): string {
  const trimmed = raw.trim();
  if (
    trimmed.length >= 2 &&
    trimmed.startsWith("\"") &&
    trimmed.endsWith("\"")
  ) {
    const inner = trimmed
      .slice(1, -1)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
    if (inner.length === 0) return "\"\"";
    return `"${inner}"`;
  }
  const tokens = trimmed
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((t) => t.length > 0);
  if (tokens.length === 0) return "\"\"";
  return tokens.map((t) => `${t}*`).join(" AND ");
}

/**
 * Viewer submitted search: quote whitespace terms for complete-query matching.
 */
export function buildQuotedTermFtsQuery(input: string): string {
  return input
    .split(/\s+/)
    .map((term) => term.replace(/"/g, ""))
    .filter((term) => term.length > 0)
    .map((term) => `"${term}"`)
    .join(" AND ");
}

/**
 * Viewer suggestions: quote terms but allow FTS5 prefix matching while typing.
 */
export function buildQuotedPrefixFtsQuery(input: string): string {
  return input
    .split(/\s+/)
    .map((term) => term.replace(/["*]/g, ""))
    .filter((term) => term.length > 0)
    .map((term) => `"${term}"*`)
    .join(" AND ");
}
