import { existsSync, statSync } from "node:fs";
import { join } from "node:path";

export const RUNTIME_DIR = ".almanac";
export const CANONICAL_WIKI_DIR = join("docs", "almanac");
export const TOPICS_YAML = "topics.yaml";
export const INDEX_DB = "index.db";

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

export function hasCanonicalWikiDir(repoRoot: string): boolean {
  return isDirectory(canonicalWikiDir(repoRoot));
}

export function indexDbPath(repoRoot: string): string {
  return join(runtimeDir(repoRoot), INDEX_DB);
}

export function canonicalTopicsYamlPath(repoRoot: string): string {
  return join(canonicalWikiDir(repoRoot), TOPICS_YAML);
}

/**
 * Return wiki content roots in precedence order.
 */
export function wikiPageRoots(repoRoot: string): WikiPageRoot[] {
  const canonical = canonicalWikiDir(repoRoot);
  return isDirectory(canonical)
    ? [{ dir: canonical, label: CANONICAL_WIKI_DIR }]
    : [];
}

export function topicsYamlPaths(repoRoot: string): string[] {
  const canonical = canonicalTopicsYamlPath(repoRoot);
  return existsSync(canonical) ? [canonical] : [];
}

function isDirectory(path: string): boolean {
  try {
    return statSync(path).isDirectory();
  } catch {
    return false;
  }
}
