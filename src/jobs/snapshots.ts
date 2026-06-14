import { createHash } from "node:crypto";
import { existsSync, statSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { basename, join } from "node:path";

import fg from "fast-glob";

import { toKebabCase } from "../slug.js";
import { wikiPageRoots, type WikiPageRoot } from "../wiki/locations.js";
import { parseFrontmatter } from "../wiki/indexer/frontmatter.js";

export interface PageSnapshotEntry {
  slug: string;
  hash: string;
}

export type PageSnapshot = Map<string, PageSnapshotEntry>;

export interface PageSnapshotDelta {
  created: string[];
  updated: string[];
  deleted: string[];
}

export async function snapshotPages(pagesDir: string): Promise<PageSnapshot> {
  return snapshotPageRoots([{ dir: pagesDir, label: pagesDir }]);
}

export async function snapshotWikiPages(repoRoot: string): Promise<PageSnapshot> {
  return snapshotPageRoots(wikiPageRoots(repoRoot));
}

async function snapshotPageRoots(
  pageRoots: WikiPageRoot[],
): Promise<PageSnapshot> {
  const out: PageSnapshot = new Map();

  for (const root of pageRoots) {
    if (!existsSync(root.dir)) continue;
    let entries: string[];
    try {
      entries = await fg("**/*.md", {
        cwd: root.dir,
        absolute: false,
        onlyFiles: true,
      });
    } catch {
      continue;
    }

    for (const entry of entries) {
      const full = join(root.dir, entry);
      try {
        const st = statSync(full);
        if (!st.isFile()) continue;
        const content = await readFile(full, "utf8");
        const fm = parseFrontmatter(content);
        const slug = toKebabCase(fm.page_id ?? basename(entry, ".md"));
        if (slug.length === 0 || out.has(slug)) continue;
        out.set(slug, {
          slug,
          hash: createHash("sha256").update(content).digest("hex"),
        });
      } catch {
        continue;
      }
    }
  }

  return out;
}

export function diffPageSnapshots(
  before: PageSnapshot,
  after: PageSnapshot,
): PageSnapshotDelta {
  const created: string[] = [];
  const updated: string[] = [];
  const deleted: string[] = [];

  for (const [slug, entry] of after) {
    const prev = before.get(slug);
    if (prev === undefined) {
      created.push(slug);
      continue;
    }
    if (prev.hash !== entry.hash) updated.push(slug);
  }

  for (const slug of before.keys()) {
    if (!after.has(slug)) deleted.push(slug);
  }

  return {
    created: created.sort(),
    updated: updated.sort(),
    deleted: deleted.sort(),
  };
}

export function isNoopPageDelta(delta: PageSnapshotDelta): boolean {
  return (
    delta.created.length === 0 &&
    delta.updated.length === 0 &&
    delta.deleted.length === 0
  );
}
