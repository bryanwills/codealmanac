import { join } from "node:path";

import type Database from "better-sqlite3";

import { ensureFreshIndex } from "../../../stores/wiki/indexer/index.js";
import { openIndex } from "../../../stores/wiki/indexer/schema.js";

export async function withFreshViewerDb<T>(
  repoRoot: string,
  fn: (db: Database.Database) => T | Promise<T>,
): Promise<T> {
  await ensureFreshIndex({ repoRoot });
  const db = openIndex(join(repoRoot, ".almanac", "index.db"));
  try {
    return await fn(db);
  } finally {
    db.close();
  }
}
