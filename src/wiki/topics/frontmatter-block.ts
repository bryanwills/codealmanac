export interface SplitFrontmatter {
  /** The opening `---\n` or `---\r\n`. */
  opener: string;
  /** Frontmatter lines (no line-ending character included). */
  fmLines: string[];
  /** The closing `---\n` (or `---\r\n`, possibly without trailing newline if EOF). */
  closer: string;
  /** Everything after the closing fence, byte-for-byte. */
  body: string;
  /**
   * Dominant line ending inside the frontmatter block. CRLF-authored
   * files stay CRLF on write; LF stays LF. We sniff once at split time
   * so rewriting doesn't have to re-inspect every line.
   */
  eol: "\n" | "\r\n";
}

/**
 * Split a file into (opener, frontmatter lines, closer, body). The
 * regex mirrors `parseFrontmatter` in `indexer/frontmatter.ts` so the
 * indexer and the rewriter agree on what "has frontmatter" means.
 *
 * Returns `null` when the file doesn't start with a `---` fence or
 * lacks a matching closer — both cases are legal (a page with only
 * body content) and the caller treats them as "no frontmatter to
 * rewrite".
 */
export function splitFrontmatter(raw: string): SplitFrontmatter | null {
  if (!raw.startsWith("---")) return null;
  // Match the exact opener (with its line ending) so we can preserve
  // it byte-for-byte.
  const openerMatch = raw.match(/^---(\r?\n)/);
  if (openerMatch === null) return null;
  const opener = `---${openerMatch[1] ?? "\n"}`;
  const rest = raw.slice(opener.length);
  // Find the closing `---` that begins at the start of a line. We
  // also handle the edge case where the closer sits at position 0 of
  // `rest` (frontmatter was empty).
  let fenceIdx: number;
  if (rest.startsWith("---")) {
    fenceIdx = 0;
  } else {
    const m = rest.match(/\r?\n---(\r?\n|$)/);
    if (m === null || m.index === undefined) return null;
    // `m.index` points at the `\r?\n` before `---`; skip that newline
    // so fenceIdx lands exactly on the `-`.
    const leadingNewlineLen = (m[0] ?? "").startsWith("\r\n") ? 2 : 1;
    fenceIdx = m.index + leadingNewlineLen;
  }
  const fmBlock = rest.slice(0, fenceIdx);
  // Determine the closer's full span, including its trailing newline if any.
  const afterDashes = rest.slice(fenceIdx + 3);
  let closerTail = "";
  if (afterDashes.startsWith("\r\n")) {
    closerTail = "\r\n";
  } else if (afterDashes.startsWith("\n")) {
    closerTail = "\n";
  }
  const closer = `---${closerTail}`;
  const body = afterDashes.slice(closerTail.length);
  const fmLines =
    fmBlock.length === 0 ? [] : fmBlock.replace(/\r?\n$/, "").split(/\r?\n/);
  // Sniff the frontmatter's dominant line ending. We look at the
  // opener first (most reliable signal — it's always present and
  // always has an ending). Fall back to checking the fmBlock for any
  // `\r\n` runs so a frontmatter with a single-line opener and
  // multi-line body still gets classified right.
  const eol: "\n" | "\r\n" =
    opener.endsWith("\r\n") || /\r\n/.test(fmBlock) ? "\r\n" : "\n";
  return { opener, fmLines, closer, body, eol };
}
