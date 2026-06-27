import { BLUE, DIM, RST } from "../../../ansi.js";
import type { WikiTopicRecord } from "../../../services/wiki/topics.js";

export function formatShow(r: WikiTopicRecord): string {
  const lines: string[] = [];
  lines.push(`${DIM}slug:${RST}         ${BLUE}${r.slug}${RST}`);
  lines.push(`${DIM}title:${RST}        ${r.title}`);
  lines.push(`${DIM}description:${RST}  ${r.description ?? "—"}`);
  lines.push(
    `${DIM}parents:${RST}      ${r.parents.length > 0 ? r.parents.join(", ") : "—"}`,
  );
  lines.push(
    `${DIM}children:${RST}     ${r.children.length > 0 ? r.children.join(", ") : "—"}`,
  );
  const pagesLabel = r.descendants_used === true
    ? "pages (incl. descendants)"
    : "pages";
  lines.push(`${DIM}${pagesLabel}:${RST}`);
  if (r.pages.length === 0) {
    lines.push("  —");
  } else {
    for (const p of r.pages) lines.push(`  ${BLUE}${p}${RST}`);
  }
  return `${lines.join("\n")}\n`;
}
