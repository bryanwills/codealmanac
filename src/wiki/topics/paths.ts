import { existsSync } from "node:fs";

import {
  canonicalWikiDir,
  canonicalTopicsYamlPath,
  indexDbPath as repoIndexDbPath,
  legacyTopicsYamlPath,
} from "../locations.js";

/**
 * `docs/almanac/topics.yaml` inside a given repo root. Single helper so no
 * caller has to remember where the file lives.
 */
export function topicsYamlPath(repoRoot: string): string {
  const canonical = canonicalTopicsYamlPath(repoRoot);
  if (existsSync(canonical)) return canonical;

  const legacy = legacyTopicsYamlPath(repoRoot);
  if (existsSync(legacy)) return legacy;

  return existsSync(canonicalWikiDir(repoRoot)) ? canonical : legacy;
}

/**
 * `.almanac/index.db` inside a given repo root. Mirrors `topicsYamlPath`
 * so the topics commands don't have to import from scattered places.
 */
export function indexDbPath(repoRoot: string): string {
  return repoIndexDbPath(repoRoot);
}
