import { existsSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, isAbsolute, join, resolve } from "node:path";

import {
  CANONICAL_WIKI_DIR,
  RUNTIME_DIR,
  TOPICS_YAML,
} from "./wiki/locations.js";

/**
 * Absolute path to the user-level `~/.almanac/` directory.
 *
 * All global state (the registry, future global config) lives here, not in
 * the repo. We resolve this via `os.homedir()` rather than `$HOME` so the
 * CLI behaves the same on macOS, Linux, and Windows.
 */
export function getGlobalAlmanacDir(): string {
  return join(homedir(), ".almanac");
}

/**
 * Absolute path to the global registry file.
 *
 * The registry is the single source of truth for "which wikis exist on this
 * machine." It is intentionally stored outside any repo so it survives
 * branch switches, clones, and repo deletions.
 */
export function getRegistryPath(): string {
  return join(getGlobalAlmanacDir(), "registry.json");
}

/**
 * Repo-level `.almanac/` path for a given working directory (not resolved —
 * just `join(cwd, ".almanac")`). Use `findNearestAlmanacDir` when you need
 * to walk upward like git does.
 */
export function getRepoAlmanacDir(cwd: string): string {
  return join(cwd, RUNTIME_DIR);
}

/**
 * True when `repoRoot` has either the legacy/runtime marker or the canonical
 * tracked docs wiki marker.
 *
 * `docs/almanac/README.md` and `docs/almanac/topics.yaml` are used as markers
 * instead of the directory alone so a random empty `docs/almanac/` folder does
 * not automatically become a wiki root.
 */
export function hasRepoAlmanacMarker(repoRoot: string): boolean {
  const runtime = join(repoRoot, RUNTIME_DIR);
  if (runtime !== getGlobalAlmanacDir() && existsSync(runtime)) {
    return true;
  }
  return (
    existsSync(join(repoRoot, CANONICAL_WIKI_DIR, "README.md")) ||
    existsSync(join(repoRoot, CANONICAL_WIKI_DIR, TOPICS_YAML))
  );
}

/**
 * Walk upward from `startDir` looking for a directory that contains an Almanac
 * wiki marker. Returns the absolute path to the repo root, or `null` if none
 * is found before hitting the filesystem root.
 *
 * Mirrors how `git` locates the enclosing repository. This lets `almanac`
 * work from any subdirectory inside a repo, not just the root.
 *
 * We explicitly skip the global `~/.almanac/` directory. It shares the
 * `.almanac` name with the per-repo wiki dir, but it's not a wiki — it
 * only holds the registry and global state. If the user runs `almanac
 * init` anywhere inside their home directory (outside a real wiki), we
 * must NOT treat `~` as an enclosing wiki root. Otherwise init would try
 * to register the home dir itself as a wiki.
 */
export function findNearestAlmanacDir(startDir: string): string | null {
  const globalDir = getGlobalAlmanacDir();
  let current = isAbsolute(startDir) ? startDir : resolve(startDir);

  // Walk until we hit the filesystem root. `dirname("/")` returns `"/"`,
  // so the loop terminates when we stop ascending.
  while (true) {
    const candidate = join(current, RUNTIME_DIR);
    if (
      (candidate !== globalDir && existsSync(candidate)) ||
      existsSync(join(current, CANONICAL_WIKI_DIR, "README.md")) ||
      existsSync(join(current, CANONICAL_WIKI_DIR, TOPICS_YAML))
    ) {
      return current;
    }
    const parent = dirname(current);
    if (parent === current) {
      return null;
    }
    current = parent;
  }
}
