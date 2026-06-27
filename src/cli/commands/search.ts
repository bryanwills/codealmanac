import { BLUE, RST } from "../../ansi.js";
import {
  searchWikiPages,
  type WikiSearchResult,
} from "../../services/wiki/search.js";

export interface SearchOptions {
  cwd: string;
  query?: string;
  topics: string[];
  mentions?: string;
  since?: string;
  stale?: string;
  orphan?: boolean;
  includeArchive?: boolean;
  archived?: boolean;
  wiki?: string;
  output?: SearchOutputMode;
  limit?: number;
}

export type SearchOutputMode = "slugs" | "summaries" | "json";

export type SearchResult = WikiSearchResult;

export interface SearchCommandOutput {
  stdout: string;
  stderr: string;
  exitCode: number;
}

/**
 * `almanac search` — the core query surface.
 *
 * This command adapter resolves the target wiki, opens a fresh index,
 * delegates query mechanics to `wiki/query`, and renders the selected
 * output shape.
 */
export async function runSearch(
  options: SearchOptions,
): Promise<SearchCommandOutput> {
  const rows = await searchWikiPages(options);
  const limited =
    options.limit !== undefined && options.limit >= 0
      ? rows.slice(0, options.limit)
      : rows;

  const stdout = formatResults(limited, options);
  const stderr = buildStderr(limited, options);
  return { stdout, stderr, exitCode: 0 };
}

function formatResults(
  rows: SearchResult[],
  options: SearchOptions,
): string {
  const output = options.output ?? "slugs";
  if (output === "json") {
    return `${JSON.stringify(rows, null, 2)}\n`;
  }
  // Empty result = empty output (not "no results found") — makes piping
  // into xargs / subsequent commands degrade gracefully.
  if (rows.length === 0) return "";
  if (output === "slugs") {
    return `${rows.map((r) => `${BLUE}${r.slug}${RST}`).join("\n")}\n`;
  }
  return `${rows.map(formatSearchResult).join("\n")}\n`;
}

function formatSearchResult(row: SearchResult): string {
  const head = `${BLUE}${row.slug}${RST}`;
  if (row.summary === null || row.summary.trim().length === 0) return head;
  return `${head}\n  ${row.summary.trim()}`;
}

function buildStderr(rows: SearchResult[], options: SearchOptions): string {
  // Spec: "print warns if >50 when not --json". The warning goes to
  // stderr so it doesn't corrupt pipelines that filter stdout.
  if (options.output === "json") return "";
  // Empty-result breadcrumb (v0.1.3). Interviews showed users saw blank
  // stdout and concluded the wiki was broken rather than the query
  // genuinely matched nothing. A single `# 0 results` line to stderr
  // makes the outcome legible without corrupting stdout pipelines (the
  // downstream command still sees zero lines). `--json` mode is silent
  // because `[]` is the unambiguous empty signal there.
  if (rows.length === 0) {
    return "# 0 results\n";
  }
  if (options.limit !== undefined) return "";
  if (rows.length > 50) {
    return `almanac: ${rows.length} results — consider --limit or a narrower query\n`;
  }
  return "";
}
