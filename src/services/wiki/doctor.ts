import { existsSync, readdirSync, statSync } from "node:fs";
import path from "node:path";

import type Database from "better-sqlite3";

import { findNearestAlmanacDir } from "../../paths.js";
import { formatDuration } from "../../shared/duration.js";
import { findEntry } from "../../stores/wiki-registry/index.js";
import {
  collectHealthReport,
  type HealthReport,
} from "../../wiki/health/index.js";
import { ensureFreshIndex } from "../../wiki/indexer/index.js";
import { openIndex } from "../../wiki/indexer/schema.js";

export type CollectWikiHealthReport = typeof collectHealthReport;

export interface WikiDoctorOptions {
  cwd: string;
  collectHealthReportFn?: CollectWikiHealthReport;
  now?: () => Date;
}

export type WikiDoctorCheckStatus = "ok" | "problem" | "info";

export interface WikiDoctorCheck {
  status: WikiDoctorCheckStatus;
  message: string;
  fix?: string;
  key: string;
}

export async function gatherWikiDoctorChecks(
  options: WikiDoctorOptions,
): Promise<WikiDoctorCheck[]> {
  const checks: WikiDoctorCheck[] = [];
  const repoRoot = findNearestAlmanacDir(options.cwd);

  if (repoRoot === null) {
    checks.push({
      status: "info",
      key: "wiki.none",
      message: "No wiki in current directory",
      fix: "run: almanac init  (to create one in this repo)",
    });
    return checks;
  }

  checks.push({
    status: "info",
    key: "wiki.repo",
    message: `repo: ${repoRoot}`,
  });

  try {
    await ensureFreshIndex({ repoRoot });
  } catch {
    // non-fatal: counts below and the health probe report any real issue.
  }

  checks.push(await describeRegistry(repoRoot));

  const almanacDir = path.join(repoRoot, ".almanac");
  const dbPath = path.join(almanacDir, "index.db");
  checks.push(...describeCounts(dbPath));
  checks.push(describeIndexFreshness(dbPath));
  checks.push(describeLastAbsorb(almanacDir, options.now));
  checks.push(await describeHealth(repoRoot, options));

  return checks;
}

async function describeRegistry(repoRoot: string): Promise<WikiDoctorCheck> {
  try {
    const entry = await findEntry({ path: repoRoot });
    if (entry !== null) {
      return {
        status: "ok",
        key: "wiki.registered",
        message: `registered as '${entry.name}'`,
      };
    }
    return {
      status: "info",
      key: "wiki.registered",
      message: "not yet registered (will register on first command)",
    };
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return {
      status: "problem",
      key: "wiki.registered",
      message: `could not read registry: ${msg}`,
      fix: "inspect ~/.almanac/registry.json; remove or fix the malformed entry",
    };
  }
}

function describeCounts(dbPath: string): WikiDoctorCheck[] {
  const checks: WikiDoctorCheck[] = [];
  let pageCount: number | null = null;
  let topicCount: number | null = null;

  if (existsSync(dbPath)) {
    try {
      const db = openIndex(dbPath);
      try {
        pageCount = countRows(db, "pages");
        topicCount = countRows(db, "topics");
      } finally {
        db.close();
      }
    } catch {
      pageCount = null;
    }
  }

  if (pageCount !== null) {
    checks.push({
      status: "info",
      key: "wiki.pages",
      message: `pages: ${pageCount}`,
    });
  }
  if (topicCount !== null) {
    checks.push({
      status: "info",
      key: "wiki.topics",
      message: `topics: ${topicCount}`,
    });
  }

  return checks;
}

function countRows(db: Database.Database, table: string): number {
  const row = db
    .prepare<[], { n: number }>(`SELECT COUNT(*) AS n FROM ${table}`)
    .get();
  return row?.n ?? 0;
}

function describeIndexFreshness(dbPath: string): WikiDoctorCheck {
  if (!existsSync(dbPath)) {
    return {
      status: "info",
      key: "wiki.index",
      message: "index: not built yet (run any query command)",
    };
  }
  try {
    const dbMtime = statSync(dbPath).mtimeMs;
    const age = Date.now() - dbMtime;
    return {
      status: "info",
      key: "wiki.index",
      message: `index: rebuilt ${formatDuration(age)} ago`,
    };
  } catch {
    return {
      status: "info",
      key: "wiki.index",
      message: "index: present",
    };
  }
}

function describeLastAbsorb(
  almanacDir: string,
  nowFn?: () => Date,
): WikiDoctorCheck {
  if (!existsSync(almanacDir)) {
    return {
      status: "info",
      key: "wiki.absorb",
      message: "last absorb: never",
    };
  }
  const logDirs = [path.join(almanacDir, "logs"), almanacDir];
  const absorbs = logDirs
    .flatMap((dir) => {
      let entries: string[];
      try {
        entries = readdirSync(dir);
      } catch {
        return [];
      }
      return entries
        .filter(
          (entry) =>
            entry.startsWith(".absorb-") &&
            (entry.endsWith(".log") || entry.endsWith(".jsonl")),
        )
        .map((entry) => ({ dir, name: entry }));
    })
    .map((entry) => {
      try {
        return {
          name: entry.name,
          mtime: statSync(path.join(entry.dir, entry.name)).mtimeMs,
        };
      } catch {
        return null;
      }
    })
    .filter((entry): entry is { name: string; mtime: number } => entry !== null);
  if (absorbs.length === 0) {
    return {
      status: "info",
      key: "wiki.absorb",
      message: "last absorb: never",
    };
  }
  absorbs.sort((a, b) => b.mtime - a.mtime);
  const latest = absorbs[0]!;
  const now = (nowFn?.() ?? new Date()).getTime();
  const age = now - latest.mtime;
  return {
    status: "info",
    key: "wiki.absorb",
    message: `last absorb: ${formatDuration(age)} ago (${latest.name})`,
  };
}

async function describeHealth(
  repoRoot: string,
  options: WikiDoctorOptions,
): Promise<WikiDoctorCheck> {
  const healthFn = options.collectHealthReportFn ?? collectHealthReport;
  try {
    const report = await healthFn({ repoRoot });
    const problems = countHealthProblems(report);
    if (problems === 0) {
      return {
        status: "ok",
        key: "wiki.health",
        message: "almanac health reports 0 problems",
      };
    }
    return {
      status: "problem",
      key: "wiki.health",
      message: `almanac health reports ${problems} problem${problems === 1 ? "" : "s"}`,
      fix: "run: almanac health",
    };
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return {
      status: "info",
      key: "wiki.health",
      message: `could not run almanac health: ${msg}`,
    };
  }
}

const HEALTH_PROBLEM_KEYS: (keyof HealthReport)[] = [
  "orphans",
  "stale",
  "dead_refs",
  "broken_links",
  "broken_xwiki",
  "empty_topics",
  "empty_pages",
  "slug_collisions",
];

function countHealthProblems(report: Partial<HealthReport>): number {
  let total = 0;
  for (const key of HEALTH_PROBLEM_KEYS) {
    const value = report[key];
    if (Array.isArray(value)) total += value.length;
  }
  return total;
}
