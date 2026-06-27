import { BLUE, DIM, RST } from "../../../ansi.js";
import type {
  WikiTopicRecord,
  WikiTopicResult,
  WikiTopicSummary,
} from "../../../services/wiki/topics.js";
import { formatTextTable } from "../table.js";
import type { TopicsCommandOutput } from "./types.js";

export function renderTopicsList(
  rows: WikiTopicSummary[],
  json?: boolean,
): TopicsCommandOutput {
  if (json === true) return ok(`${JSON.stringify(rows, null, 2)}\n`);

  if (rows.length === 0) {
    return ok(
      "no topics. create one with `almanac topics create <name>` or tag a page.\n",
    );
  }

  const lines = formatTextTable({
    headers: ["TOPIC", "PAGES"],
    rows: rows.map((row) => [
      `${BLUE}${row.slug}${RST}`,
      `${DIM}${formatPageCount(row.page_count)}${RST}`,
    ]),
  });
  return ok(`${lines.join("\n")}\n`);
}

export function renderTopicsShow(
  result: WikiTopicResult,
  json?: boolean,
): TopicsCommandOutput {
  switch (result.status) {
    case "found":
      return ok(
        json === true
          ? `${JSON.stringify(result.topic, null, 2)}\n`
          : formatTopicRecord(result.topic),
      );
    case "empty-slug":
      return error("almanac: empty topic slug\n");
    case "missing":
      return error(`almanac: no such topic "${result.slug}"\n`);
  }
}

function formatTopicRecord(record: WikiTopicRecord): string {
  const lines: string[] = [];
  lines.push(`${DIM}slug:${RST}         ${BLUE}${record.slug}${RST}`);
  lines.push(`${DIM}title:${RST}        ${record.title}`);
  lines.push(`${DIM}description:${RST}  ${record.description ?? "—"}`);
  lines.push(`${DIM}parents:${RST}      ${formatTopicList(record.parents)}`);
  lines.push(`${DIM}children:${RST}     ${formatTopicList(record.children)}`);
  const pagesLabel = record.descendants_used === true
    ? "pages (incl. descendants)"
    : "pages";
  lines.push(`${DIM}${pagesLabel}:${RST}`);
  if (record.pages.length === 0) {
    lines.push("  —");
  } else {
    for (const page of record.pages) lines.push(`  ${BLUE}${page}${RST}`);
  }
  return `${lines.join("\n")}\n`;
}

function formatTopicList(slugs: string[]): string {
  return slugs.length > 0 ? slugs.join(", ") : "—";
}

function formatPageCount(pageCount: number): string {
  return `(${pageCount} page${pageCount === 1 ? "" : "s"})`;
}

function ok(stdout: string): TopicsCommandOutput {
  return { stdout, stderr: "", exitCode: 0 };
}

function error(stderr: string): TopicsCommandOutput {
  return { stdout: "", stderr, exitCode: 1 };
}
