import { existsSync, readdirSync } from "node:fs";
import path from "node:path";

import {
  blue,
  bold,
  dim,
  renderNextStepsBox,
  type SetupTheme,
} from "./output.js";

/**
 * Print the "Next steps" box. When `existingPageCount` is greater than 0,
 * the current working directory already has a wiki with committed pages.
 * In that case we skip the `almanac init` step and tell the user to
 * start querying.
 */
export function printNextSteps(
  out: NodeJS.WritableStream,
  theme: SetupTheme,
  existingPageCount: number,
  mode: "hosted" | "self-managed" = "hosted",
): void {
  if (mode === "self-managed") {
    renderNextStepsBox(out, theme, [
      numbered(theme, 1, "Local automations are running:"),
      command(theme, "almanac sync --quiet 45m"),
      command(theme, "almanac garden"),
      numbered(theme, 2, "Query locally:"),
      command(theme, 'almanac search "auth"'),
      command(theme, "almanac search --mentions <file>"),
    ]);
    return;
  } else if (existingPageCount > 0) {
    renderNextStepsBox(out, theme, [
      existingWikiLine(theme, existingPageCount),
      "",
      numbered(theme, 1, "Start querying it locally:"),
      command(theme, "almanac search --mentions <file>"),
      command(theme, 'almanac search "auth"'),
      numbered(theme, 2, "Read one of the result pages:"),
      command(theme, "almanac show <result-slug>"),
    ]);
    return;
  }

  renderNextStepsBox(out, theme, [
    numbered(theme, 1, "Create this repo's wiki from the dashboard:"),
    command(theme, "https://codealmanac.com/dashboard"),
    numbered(theme, 2, "After .almanac/ lands, query locally:"),
    command(theme, 'almanac search "auth"'),
  ]);
}

function numbered(theme: SetupTheme, n: number, text: string): string {
  return `  ${blue(theme, `${n}.`)}  ${text}`;
}

function command(theme: SetupTheme, text: string): string {
  return `       ${bold(theme, text)}`;
}

function existingWikiLine(theme: SetupTheme, existingPageCount: number): string {
  const plural = existingPageCount === 1 ? "" : "s";
  return `  ${blue(theme, "\u25c7")}  This repo already has a wiki ${dim(
    theme,
    `(${existingPageCount} page${plural})`,
  )}`;
}

/**
 * Count `.md` files in `.almanac/pages/` under the current working
 * directory or any parent. Returns 0 when no wiki is found or the pages
 * directory is empty.
 */
export function countExistingPages(cwd: string): number {
  try {
    let dir = cwd;
    for (let i = 0; i < 10; i++) {
      const pagesDir = path.join(dir, ".almanac", "pages");
      if (existsSync(pagesDir)) {
        try {
          const entries = readdirSync(pagesDir);
          return entries.filter((e) => e.endsWith(".md")).length;
        } catch {
          return 0;
        }
      }
      const parent = path.dirname(dir);
      if (parent === dir) break;
      dir = parent;
    }
  } catch {
    // Swallow — never crash setup because of this.
  }
  return 0;
}
