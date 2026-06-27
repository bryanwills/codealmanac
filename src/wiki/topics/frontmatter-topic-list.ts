import yaml from "js-yaml";

export interface ExistingRange {
  /** Index in `fmLines` of the `topics:` key line (inclusive). */
  start: number;
  /** Index in `fmLines` one past the last line belonging to this key. */
  end: number;
  /**
   * Lines inside `[start+1, end)` that aren't `- entry` lines — i.e.
   * interleaved comments and blank lines a user wrote between entries.
   * We preserve these verbatim when rewriting block-style lists to
   * flow; otherwise a `tag` on a commented list would silently drop
   * the commentary. Empty for flow/scalar shapes.
   */
  preserved: string[];
}

/**
 * Find `topics:` in a frontmatter-lines array and read the values.
 *
 * Handles three YAML shapes authors commonly write:
 *   - `topics: [a, b, c]`       (flow sequence, one line)
 *   - `topics:` followed by block entries like `  - a` (block sequence)
 *   - `topics: a` (a single scalar — treated as one element)
 *
 * Also handles the empty case `topics:` with nothing after it, and the
 * "no topics key" case (returns `existingRange: null`).
 *
 * This is NOT a general YAML parser — it's intentionally scoped to the
 * one key we mutate, because using `js-yaml` for a round-trip would
 * lose comments and re-quote strings the user picked a specific way.
 */
export function readTopicsFromLines(fmLines: string[]): {
  before: string[];
  existingRange: ExistingRange | null;
} {
  const keyLineIdx = findTopKey(fmLines, "topics");
  if (keyLineIdx === -1) {
    return { before: [], existingRange: null };
  }
  const keyLine = fmLines[keyLineIdx] ?? "";
  const colonIdx = keyLine.indexOf(":");
  const after = keyLine.slice(colonIdx + 1).trim();
  const afterNoComment = stripTrailingComment(after);

  if (afterNoComment.length === 0) {
    return readBlockTopics(fmLines, keyLineIdx);
  }

  let parsed: unknown;
  try {
    parsed = yaml.load(afterNoComment);
  } catch {
    parsed = null;
  }
  const values: string[] = [];
  if (Array.isArray(parsed)) {
    for (const v of parsed) {
      if (typeof v === "string" && v.trim().length > 0) {
        values.push(v.trim());
      }
    }
  } else if (typeof parsed === "string" && parsed.trim().length > 0) {
    values.push(parsed.trim());
  }
  return {
    before: values,
    existingRange: { start: keyLineIdx, end: keyLineIdx + 1, preserved: [] },
  };
}

function readBlockTopics(
  fmLines: string[],
  keyLineIdx: number,
): { before: string[]; existingRange: ExistingRange } {
  const values: string[] = [];
  const preserved: string[] = [];
  let i = keyLineIdx + 1;
  let endIdx = i;
  let pendingNonEntries: string[] = [];

  while (i < fmLines.length) {
    const line = fmLines[i] ?? "";
    const trimmed = line.trim();
    if (trimmed.length === 0 || trimmed.startsWith("#")) {
      pendingNonEntries.push(line);
      i += 1;
      continue;
    }
    const m = line.match(/^\s*-\s+(.*)$/);
    if (m === null) break;
    if (pendingNonEntries.length > 0) {
      preserved.push(...pendingNonEntries);
      pendingNonEntries = [];
    }
    const raw = stripTrailingComment((m[1] ?? "").trim());
    const parsed = parseScalar(raw);
    if (parsed.length > 0) values.push(parsed);
    i += 1;
    endIdx = i;
  }

  return {
    before: values,
    existingRange: { start: keyLineIdx, end: endIdx, preserved },
  };
}

function findTopKey(fmLines: string[], key: string): number {
  const re = new RegExp(`^${escapeRegex(key)}\\s*:`);
  for (let i = 0; i < fmLines.length; i += 1) {
    if (re.test(fmLines[i] ?? "")) return i;
  }
  return -1;
}

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function stripTrailingComment(s: string): string {
  let inSingle = false;
  let inDouble = false;
  for (let i = 0; i < s.length; i += 1) {
    const ch = s[i];
    if (ch === "'" && !inDouble) inSingle = !inSingle;
    else if (ch === '"' && !inSingle) inDouble = !inDouble;
    else if (ch === "#" && !inSingle && !inDouble) {
      return s.slice(0, i).trimEnd();
    }
  }
  return s;
}

function parseScalar(s: string): string {
  if (s.length === 0) return s;
  if (s.length >= 2 && s[0] === '"' && s[s.length - 1] === '"') {
    return s.slice(1, -1);
  }
  if (s.length >= 2 && s[0] === "'" && s[s.length - 1] === "'") {
    return s.slice(1, -1);
  }
  return s;
}

export function flowList(items: string[]): string {
  return `[${items.map((t) => formatScalar(t)).join(", ")}]`;
}

function formatScalar(s: string): string {
  if (/^[a-z0-9][a-z0-9-]*$/.test(s)) return s;
  return yaml
    .dump(s, { flowLevel: 0, lineWidth: Number.MAX_SAFE_INTEGER })
    .trimEnd();
}

export function dedupeSlugs(list: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const raw of list) {
    const s = raw.trim();
    if (s.length === 0) continue;
    if (seen.has(s)) continue;
    seen.add(s);
    out.push(s);
  }
  return out;
}

export function arraysEqual(a: string[], b: string[]): boolean {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i += 1) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}
