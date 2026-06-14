import { readdirSync } from "node:fs";
import path from "node:path";

import { findNearestAlmanacDir } from "../../../paths.js";
import { wikiPageRoots } from "../../../wiki/locations.js";

const RST = "\x1b[0m";
const BOLD = "\x1b[1m";
const DIM = "\x1b[2m";
const WHITE_BOLD = "\x1b[1;37m";
const BLUE = "\x1b[38;5;75m";
const BLUE_DIM = "\x1b[38;5;69m";

/**
 * Print the "Next steps" box. When `existingPageCount` is greater than 0,
 * the current working directory already has a wiki with committed pages.
 * In that case we skip the `almanac init` step and tell the user to
 * start querying.
 */
export function printNextSteps(
  out: NodeJS.WritableStream,
  existingPageCount: number,
): void {
  const innerW = 62;
  const vis = (s: string): number =>
    s.replace(/\x1b\[[0-9;]*m/g, "").length;
  const row = (content: string): string => {
    const padding = Math.max(0, innerW - vis(content));
    return `  ${BLUE_DIM}\u2502${RST}${content}${" ".repeat(padding)}${BLUE_DIM}\u2502${RST}\n`;
  };
  const empty = row("");

  out.write(`  ${BLUE_DIM}\u256d${"─".repeat(innerW)}\u256e${RST}\n`);
  out.write(empty);
  out.write(row(`  ${WHITE_BOLD}Next steps${RST}`));
  out.write(empty);

  if (existingPageCount > 0) {
    out.write(
      row(
        `  ${BLUE}\u25c7${RST}  This repo already has a wiki ${DIM}(${existingPageCount} page${existingPageCount === 1 ? "" : "s"})${RST}`,
      ),
    );
    out.write(empty);
    out.write(row(`  ${BLUE}1.${RST}  Start querying your wiki:`));
    out.write(row(`       ${BOLD}almanac search --mentions <file>${RST}`));
    out.write(
      row(`  ${BLUE}2.${RST}  Work normally — scheduled sync absorbs new chats`),
    );
  } else {
    out.write(
      row(`  ${BLUE}1.${RST}  ${BOLD}cd${RST} into a repo you want to document`),
    );
    out.write(
      row(
        `  ${BLUE}2.${RST}  ${BOLD}almanac init${RST}  ${DIM}# build the wiki${RST}`,
      ),
    );
    out.write(
      row(`  ${BLUE}3.${RST}  Work normally — scheduled sync absorbs new chats`),
    );
  }

  out.write(empty);
  out.write(`  ${BLUE_DIM}\u2570${"─".repeat(innerW)}\u256f${RST}\n\n`);
}

/**
 * Count `.md` wiki files under the current working directory or any parent.
 * Returns 0 when no wiki is found or the content roots are empty.
 */
export function countExistingPages(cwd: string): number {
  try {
    const repoRoot = findNearestAlmanacDir(cwd);
    if (repoRoot === null) return 0;
    return wikiPageRoots(repoRoot).reduce(
      (count, root) => count + countMarkdownFiles(root.dir),
      0,
    );
  } catch {
    // Swallow — never crash setup because of this.
  }
  return 0;
}

function countMarkdownFiles(dir: string): number {
  let count = 0;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      count += countMarkdownFiles(fullPath);
    } else if (entry.isFile() && entry.name.endsWith(".md")) {
      count += 1;
    }
  }
  return count;
}
