import { existsSync } from "node:fs";
import { join } from "node:path";

export const RUNTIME_DIR = ".almanac";
export const CANONICAL_WIKI_DIR = join("docs", "almanac");
export const LEGACY_PAGES_DIR = join(".almanac", "pages");
export const TOPICS_YAML = "topics.yaml";
export const INDEX_DB = "index.db";
export const REVIEW_YAML = "review.yaml";

export interface WikiPageRoot {
  dir: string;
  label: string;
}

export function runtimeDir(repoRoot: string): string {
  return join(repoRoot, RUNTIME_DIR);
}

export function canonicalWikiDir(repoRoot: string): string {
  return join(repoRoot, CANONICAL_WIKI_DIR);
}

export function legacyPagesDir(repoRoot: string): string {
  return join(repoRoot, LEGACY_PAGES_DIR);
}

export function indexDbPath(repoRoot: string): string {
  return join(runtimeDir(repoRoot), INDEX_DB);
}

export function canonicalTopicsYamlPath(repoRoot: string): string {
  return join(canonicalWikiDir(repoRoot), TOPICS_YAML);
}

export function legacyTopicsYamlPath(repoRoot: string): string {
  return join(runtimeDir(repoRoot), TOPICS_YAML);
}

export function reviewYamlPath(repoRoot: string): string {
  return join(runtimeDir(repoRoot), REVIEW_YAML);
}

/**
 * Return wiki content roots in precedence order.
 *
 * `docs/almanac/` is the canonical readable wiki. `.almanac/pages/` remains
 * indexed during migration so existing repos do not go dark when the new docs
 * tree is introduced.
 */
export function wikiPageRoots(repoRoot: string): WikiPageRoot[] {
  const roots: WikiPageRoot[] = [];
  const canonical = canonicalWikiDir(repoRoot);
  if (existsSync(canonical)) {
    roots.push({ dir: canonical, label: CANONICAL_WIKI_DIR });
  }

  const legacy = legacyPagesDir(repoRoot);
  if (existsSync(legacy)) {
    roots.push({ dir: legacy, label: LEGACY_PAGES_DIR });
  }

  return roots;
}

export function topicsYamlPaths(repoRoot: string): string[] {
  const canonical = canonicalTopicsYamlPath(repoRoot);
  if (existsSync(canonical)) return [canonical];

  const legacy = legacyTopicsYamlPath(repoRoot);
  return existsSync(legacy) ? [legacy] : [];
}
