import { existsSync } from "node:fs";
import { mkdir, readFile, utimes, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

import {
  acquireRunWorkerLock,
  buildQueuedRunRecord,
  buildStartedRunRecord,
  finishRunRecord,
  oldestQueuedRun,
  runRecordPath,
  runWorkerLockPath,
  writeRunRecord,
} from "../src/process/index.js";
import { makeRepo, scaffoldWiki, withTempHome } from "./helpers.js";

describe("process operation queue", () => {
  it("acquires and releases a per-wiki worker lock", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "queue-lock");
      await scaffoldWiki(repo);

      const lock = await acquireRunWorkerLock(
        repo,
        new Date(),
      );

      expect(lock).not.toBeNull();
      expect(lock?.path).toBe(runWorkerLockPath(repo));
      await expect(
        readFile(join(runWorkerLockPath(repo), "owner.json"), "utf8"),
      ).resolves.toContain(`"pid": ${process.pid}`);

      const second = await acquireRunWorkerLock(
        repo,
        new Date("2026-05-29T10:00:01.000Z"),
      );
      expect(second).toBeNull();

      await lock?.release();
      expect(existsSync(runWorkerLockPath(repo))).toBe(false);
    });
  });

  it("recovers a stale worker lock", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "queue-stale-lock");
      await scaffoldWiki(repo);
      const lockPath = runWorkerLockPath(repo);
      await mkdir(lockPath, { recursive: true });
      await writeFile(
        join(lockPath, "owner.json"),
        `${JSON.stringify({
          pid: 999_999,
          startedAt: "2026-05-29T08:00:00.000Z",
        })}\n`,
        "utf8",
      );

      const lock = await acquireRunWorkerLock(
        repo,
        new Date(),
      );

      expect(lock).not.toBeNull();
      await lock?.release();
    });
  });

  it("does not remove a new ownerless worker lock", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "queue-ownerless-lock");
      await scaffoldWiki(repo);
      const lockPath = runWorkerLockPath(repo);
      await mkdir(lockPath, { recursive: true });

      const lock = await acquireRunWorkerLock(
        repo,
        new Date(),
      );

      expect(lock).toBeNull();
      expect(existsSync(lockPath)).toBe(true);
    });
  });

  it("recovers an old ownerless worker lock", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "queue-old-ownerless-lock");
      await scaffoldWiki(repo);
      const lockPath = runWorkerLockPath(repo);
      await mkdir(lockPath, { recursive: true });
      const old = new Date(Date.now() - 60_000);
      await utimes(lockPath, old, old);

      const lock = await acquireRunWorkerLock(
        repo,
        new Date(),
      );

      expect(lock).not.toBeNull();
      await lock?.release();
    });
  });

  it("selects the oldest queued run only", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "queue-oldest");
      await scaffoldWiki(repo);

      const done = finishRunRecord({
        record: buildQueuedRunRecord({
          runId: "run_20260529100100_done",
          repoRoot: repo,
          queuedAt: new Date("2026-05-29T10:01:00.000Z"),
          spec: {
            provider: { id: "codex" },
            cwd: repo,
            prompt: "done",
            metadata: { operation: "garden" },
          },
        }),
        status: "done",
        finishedAt: new Date("2026-05-29T10:02:00.000Z"),
      });
      const running = buildStartedRunRecord({
        runId: "run_20260529100030_running",
        repoRoot: repo,
        startedAt: new Date("2026-05-29T10:00:30.000Z"),
        spec: {
          provider: { id: "codex" },
          cwd: repo,
          prompt: "running",
          metadata: { operation: "garden" },
        },
      });
      const newer = buildQueuedRunRecord({
        runId: "run_20260529100400_newer",
        repoRoot: repo,
        queuedAt: new Date("2026-05-29T10:04:00.000Z"),
        spec: {
          provider: { id: "codex" },
          cwd: repo,
          prompt: "newer",
          metadata: { operation: "garden" },
        },
      });
      const older = buildQueuedRunRecord({
        runId: "run_20260529100300_older",
        repoRoot: repo,
        queuedAt: new Date("2026-05-29T10:03:00.000Z"),
        spec: {
          provider: { id: "claude" },
          cwd: repo,
          prompt: "older",
          metadata: { operation: "absorb" },
        },
      });

      for (const record of [done, running, newer, older]) {
        await writeRunRecord(runRecordPath(repo, record.id), record);
      }

      await expect(oldestQueuedRun(repo)).resolves.toMatchObject({
        id: "run_20260529100300_older",
        status: "queued",
      });
    });
  });
});
