import { existsSync } from "node:fs";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";

import { parseJsonObject } from "./discovery/jsonl.js";
import { getRepoAlmanacDir } from "../paths.js";

const SYNC_LOCK_STALE_MS = 60 * 60 * 1000;

export function syncLockPath(repoRoot: string): string {
  return join(getRepoAlmanacDir(repoRoot), "jobs", "sync.lock");
}

function legacySyncLockPath(repoRoot: string): string {
  return join(getRepoAlmanacDir(repoRoot), "runs", "sync.lock");
}

function existingSyncLockPath(repoRoot: string): string {
  const primary = syncLockPath(repoRoot);
  if (existsSync(primary)) return primary;
  const legacy = legacySyncLockPath(repoRoot);
  return existsSync(legacy) ? legacy : primary;
}

export async function acquireRepoSyncLock(repoRoot: string, now: Date): Promise<boolean> {
  if (await tryCreateRepoLock(repoRoot, now)) return true;
  if (!await isStaleRepoLock(repoRoot, now)) return false;
  await releaseRepoSyncLock(repoRoot);
  return await tryCreateRepoLock(repoRoot, now);
}

export async function releaseRepoSyncLock(repoRoot: string): Promise<void> {
  await rm(syncLockPath(repoRoot), { recursive: true, force: true });
  await rm(legacySyncLockPath(repoRoot), { recursive: true, force: true });
}

function lockOwnerPath(repoRoot: string): string {
  return join(existingSyncLockPath(repoRoot), "owner.json");
}

async function tryCreateRepoLock(repoRoot: string, now: Date): Promise<boolean> {
  try {
    const lock = syncLockPath(repoRoot);
    await mkdir(dirname(lock), { recursive: true });
    await mkdir(lock, { recursive: false });
    await writeFile(
      lockOwnerPath(repoRoot),
      `${JSON.stringify({ pid: process.pid, startedAt: now.toISOString() }, null, 2)}\n`,
      "utf8",
    );
    return true;
  } catch {
    return false;
  }
}

async function isStaleRepoLock(repoRoot: string, now: Date): Promise<boolean> {
  let raw: Record<string, unknown> = {};
  try {
    raw = parseJsonObject(await readFile(lockOwnerPath(repoRoot), "utf8")) ?? {};
  } catch {
    return true;
  }
  const startedAt = typeof raw.startedAt === "string" ? Date.parse(raw.startedAt) : NaN;
  if (!Number.isFinite(startedAt)) return true;
  if (now.getTime() - startedAt > SYNC_LOCK_STALE_MS) return true;
  const pid = typeof raw.pid === "number" ? raw.pid : null;
  return pid !== null && !isPidAlive(pid);
}

function isPidAlive(pid: number): boolean {
  if (pid <= 0) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}
