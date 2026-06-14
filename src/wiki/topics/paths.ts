import {
  canonicalTopicsYamlPath,
  indexDbPath as repoIndexDbPath,
} from "../locations.js";

/**
 * `docs/almanac/topics.yaml` inside a given repo root. Single helper so no
 * caller has to remember where the file lives.
 */
export function topicsYamlPath(repoRoot: string): string {
  return canonicalTopicsYamlPath(repoRoot);
}

/**
 * `.almanac/index.db` inside a given repo root. Mirrors `topicsYamlPath`
 * so the topics commands don't have to import from scattered places.
 */
export function indexDbPath(repoRoot: string): string {
  return repoIndexDbPath(repoRoot);
}
