import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { basename } from "node:path";

import fg from "fast-glob";
import type Database from "better-sqlite3";

import { toKebabCase } from "../../slug.js";
import { parseFrontmatter } from "../indexer/frontmatter.js";
import { inPageScope, type HealthScope } from "./scope.js";

/**
 * Pages with zero `topics:`. Archived pages are exempt.
 */
export function findOrphans(
  db: Database.Database,
  scope: HealthScope,
): { slug: string }[] {
  const rows = db
    .prepare<[], { slug: string }>(
      `SELECT p.slug FROM pages p
       WHERE p.archived_at IS NULL
         AND NOT EXISTS (
           SELECT 1 FROM page_topics pt WHERE pt.page_slug = p.slug
         )
       ORDER BY p.slug`,
    )
    .all();
  return rows.filter((r) => inPageScope(scope, r.slug));
}

/**
 * Active pages whose `updated_at` is older than `staleSeconds`.
 */
export function findStale(
  db: Database.Database,
  scope: HealthScope,
  staleSeconds: number,
): { slug: string; days_since_update: number }[] {
  const now = Math.floor(Date.now() / 1000);
  const threshold = now - staleSeconds;
  const rows = db
    .prepare<[number], { slug: string; updated_at: number }>(
      `SELECT slug, updated_at FROM pages
       WHERE archived_at IS NULL AND updated_at < ?
       ORDER BY updated_at ASC`,
    )
    .all(threshold);
  return rows
    .filter((r) => inPageScope(scope, r.slug))
    .map((r) => ({
      slug: r.slug,
      days_since_update: Math.floor((now - r.updated_at) / (60 * 60 * 24)),
    }));
}

/** Topics with zero pages. */
export function findEmptyTopics(
  db: Database.Database,
  scope: HealthScope,
): { slug: string }[] {
  const rows = db
    .prepare<[], { slug: string }>(
      `SELECT t.slug FROM topics t
       WHERE NOT EXISTS (
         SELECT 1 FROM page_topics pt WHERE pt.topic_slug = t.slug
       )
       ORDER BY t.slug`,
    )
    .all();
  if (scope.topics === null) return rows;
  return rows.filter((r) => scope.topics!.has(r.slug));
}

/**
 * Pages whose body is effectively empty.
 */
export async function findEmptyPages(
  db: Database.Database,
  scope: HealthScope,
): Promise<{ slug: string }[]> {
  const rows = db
    .prepare<[], { slug: string; file_path: string }>(
      `SELECT slug, file_path FROM pages
       WHERE archived_at IS NULL
       ORDER BY slug`,
    )
    .all();
  const out: { slug: string }[] = [];
  for (const r of rows) {
    if (!inPageScope(scope, r.slug)) continue;
    let raw: string;
    try {
      raw = await readFile(r.file_path, "utf8");
    } catch {
      continue;
    }
    const body = parseFrontmatter(raw).body;
    const hasSubstance = body
      .split(/\r?\n/)
      .some((line) => {
        const trimmed = line.trim();
        return trimmed.length > 0 && !trimmed.startsWith("#");
      });
    if (!hasSubstance) {
      out.push({ slug: r.slug });
    }
  }
  return out;
}

/**
 * Walk `.almanac/pages/` and group filenames by their kebab-cased slug.
 */
export async function findSlugCollisions(
  pagesDir: string,
): Promise<{ slug: string; paths: string[] }[]> {
  if (!existsSync(pagesDir)) return [];
  const files = await fg("**/*.md", {
    cwd: pagesDir,
    absolute: false,
    onlyFiles: true,
    caseSensitiveMatch: true,
  });
  const bySlug = new Map<string, string[]>();
  for (const rel of files) {
    const slug = toKebabCase(basename(rel, ".md"));
    if (slug.length === 0) continue;
    const list = bySlug.get(slug) ?? [];
    list.push(rel);
    bySlug.set(slug, list);
  }
  const out: { slug: string; paths: string[] }[] = [];
  for (const [slug, paths] of bySlug.entries()) {
    if (paths.length > 1) {
      out.push({ slug, paths: paths.sort() });
    }
  }
  out.sort((a, b) => a.slug.localeCompare(b.slug));
  return out;
}
