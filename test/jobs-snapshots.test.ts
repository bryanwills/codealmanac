import { mkdir, rm, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

import {
  diffPageSnapshots,
  isNoopPageDelta,
  snapshotPages,
  snapshotWikiPages,
} from "../src/jobs/index.js";
import { makeRepo, scaffoldWiki, withTempHome, writePage } from "./helpers.js";

describe("process page snapshots", () => {
  it("returns an empty snapshot when pages directory is missing", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "missing-pages");
      await expect(snapshotPages(join(repo, ".almanac", "pages"))).resolves.toEqual(
        new Map(),
      );
    });
  });

  it("snapshots markdown pages", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "snapshot-pages");
      await scaffoldWiki(repo);
      await writePage(repo, "active", "---\ntitle: Active\n---\n# Active\n");
      await writePage(repo, "second", "---\ntitle: Second\n---\n# Second\n");
      await writeFile(join(repo, "docs", "almanac", "ignore.txt"), "x", "utf8");

      const snapshot = await snapshotPages(join(repo, "docs", "almanac"));

      expect([...snapshot.keys()].sort()).toEqual(["active", "second"]);
      expect(snapshot.get("active")?.hash).toMatch(/^[0-9a-f]{64}$/);
    });
  });

  it("snapshots canonical docs/almanac pages by page_id", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "snapshot-docs");
      const docsDir = join(repo, "docs", "almanac", "architecture");
      await mkdir(docsDir, { recursive: true });
      await writeFile(
        join(docsDir, "README.md"),
        "---\npage_id: architecture\n---\n# Architecture\n",
        "utf8",
      );

      const snapshot = await snapshotWikiPages(repo);

      expect([...snapshot.keys()]).toEqual(["architecture"]);
      expect(snapshot.get("architecture")?.hash).toMatch(/^[0-9a-f]{64}$/);
    });
  });

  it("counts created, updated, and deleted page changes", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "snapshot-delta");
      const pagesDir = await scaffoldWiki(repo);
      await writePage(repo, "updated", "# Before\n");
      await writePage(repo, "deleted", "# Delete me\n");

      const before = await snapshotPages(pagesDir);

      await writePage(repo, "updated", "# After\n");
      await writePage(repo, "created", "# New\n");
      await rm(join(pagesDir, "deleted.md"));

      const after = await snapshotPages(pagesDir);

      expect(diffPageSnapshots(before, after)).toEqual({
        created: ["created"],
        updated: ["updated"],
        deleted: ["deleted"],
      });
    });
  });

  it("detects no-op page deltas", () => {
    expect(
      isNoopPageDelta({ created: [], updated: [], deleted: [] }),
    ).toBe(true);
    expect(
      isNoopPageDelta({ created: [], updated: ["x"], deleted: [] }),
    ).toBe(false);
  });

  it("ignores unreadable directories with markdown-like names", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "snapshot-dir");
      const pagesDir = await scaffoldWiki(repo);
      await mkdir(join(pagesDir, "folder.md"));

      const snapshot = await snapshotPages(pagesDir);

      expect(snapshot.size).toBe(0);
    });
  });
});
