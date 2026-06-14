import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import {
  buildStartedJobRecord,
  finishJobRecord,
  jobLogPath,
  jobRecordPath,
  writeJobRecord,
  writeJobSpec,
} from "../src/jobs/index.js";
import { createViewerApi } from "../src/viewer/api.js";
import { makeRepo, scaffoldWiki, withTempHome, writePage } from "./helpers.js";

async function seedViewerWiki(repo: string): Promise<void> {
  await scaffoldWiki(repo);
  await writeFile(
    join(repo, "docs", "almanac", "topics.yaml"),
    `topics:
  - slug: systems
    title: Systems
    description: Custom subsystems.
    parents: []
  - slug: storage
    title: Storage
    description: Persistence layer.
    parents: [systems]
  - slug: agents
    title: Agents
    description: Agent integration.
    parents: [systems]
`,
    "utf8",
  );
  await writePage(
    repo,
    "sqlite-indexer",
    `---
title: SQLite Indexer
description: Derived search index for wiki pages.
topics: [storage, systems, agents]
sources:
  - id: indexer
    type: file
    path: src/wiki/indexer/index.ts
    note: Implements indexing.
---

# SQLite Indexer

The indexer reads [[src/wiki/indexer/index.ts]] and links to [[wikilink-syntax]].
`,
  );
  await writePage(
    repo,
    "wikilink-syntax",
    `---
title: Wikilink Syntax
topics: [systems]
sources:
  - id: indexer-folder
    type: file
    path: src/wiki/indexer/
---

# Wikilink Syntax

The syntax page links back to [[sqlite-indexer]].
`,
  );
}

describe("viewer api", () => {
  it("returns overview, page detail, search, topics, and file mentions", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "r");
      await seedViewerWiki(repo);
      const api = createViewerApi({ repoRoot: repo });

      const overview = await api.overview();
      expect(overview.pageCount).toBe(2);
      expect(overview.topicCount).toBe(3);
      expect(overview.topicNavigation).toEqual({ source: "curated", sidebarLimit: 8 });
      expect(overview.recentPages.map((p) => p.slug).sort()).toEqual([
        "sqlite-indexer",
        "wikilink-syntax",
      ]);
      expect(overview.rootTopics.map((t) => t.slug)).toEqual(["systems"]);
      expect(overview.topics.map((t) => t.slug)).toContain("agents");
      expect(overview.topics.find((t) => t.slug === "systems")?.parents).toEqual([]);
      expect(overview.topics.find((t) => t.slug === "storage")?.parents).toEqual(["systems"]);
      expect(overview.topics.find((t) => t.slug === "agents")?.parents).toEqual(["systems"]);
      expect(overview.featuredPages.frontDoor).toBeNull();

      const page = await api.page("sqlite-indexer");
      expect(page?.body).toContain("# SQLite Indexer");
      expect(page?.topics).toEqual(["agents", "storage", "systems"]);
      expect(page?.file_refs).toEqual([
        { path: "src/wiki/indexer/index.ts", is_dir: false },
      ]);
      expect(page?.sources).toEqual([
        {
          id: "indexer",
          type: "file",
          target: "src/wiki/indexer/index.ts",
          title: null,
          retrieved_at: null,
          note: "Implements indexing.",
        },
      ]);
      expect(page?.wikilinks_out).toContain("wikilink-syntax");
      expect(page?.wikilinks_in).toContain("wikilink-syntax");

      const topic = await api.topic("systems");
      expect(topic?.pages.map((p) => p.slug).sort()).toEqual([
        "sqlite-indexer",
        "wikilink-syntax",
      ]);

      const search = await api.search("Derived search");
      expect(search.pages.map((p) => p.slug)).toEqual(["sqlite-indexer"]);

      const suggestions = await api.suggest("Derived");
      expect(suggestions.pages.map((p) => p.slug)).toEqual(["sqlite-indexer"]);
      const partialSuggestions = await api.suggest("Deriv");
      expect(partialSuggestions.pages.map((p) => p.slug)).toEqual(["sqlite-indexer"]);
      await expect(api.suggest("\"")).resolves.toEqual({ query: "\"", pages: [] });

      const file = await api.file("src/wiki/indexer/index.ts");
      expect(file.pages.map((p) => p.slug).sort()).toEqual([
        "sqlite-indexer",
        "wikilink-syntax",
      ]);
    });
  });

  it("reports markdown-backed front door when docs/almanac README exists", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "r");
      await mkdir(join(repo, "docs", "almanac"), { recursive: true });
      await writeFile(
        join(repo, "docs", "almanac", "README.md"),
        "---\npage_id: custom-front-door\ntitle: Codebase Wiki\ntopics: [concepts]\n---\n\n# Codebase Wiki\n\nStart here.\n",
      );

      const api = createViewerApi({ repoRoot: repo });
      const overview = await api.overview();

      expect(overview.featuredPages.frontDoor?.slug).toBe("custom-front-door");
    });
  });

  it("marks frontmatter-only topics as tag navigation", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "r");
      await scaffoldWiki(repo);
      await writePage(
        repo,
        "tagged-page",
        "---\ntitle: Tagged Page\ntopics: [alpha, beta, gamma]\n---\n\n# Tagged Page\n\nBody.\n",
      );

      const api = createViewerApi({ repoRoot: repo });
      const overview = await api.overview();

      expect(overview.topicNavigation).toEqual({ source: "tags", sidebarLimit: 8 });
      expect(overview.topics.map((topic) => topic.slug).sort()).toEqual(["alpha", "beta", "gamma"]);
    });
  });

  it("limits overview root topics for tag-only wikis", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "r");
      await scaffoldWiki(repo);
      for (let i = 0; i < 10; i++) {
        await writePage(
          repo,
          `tagged-page-${i}`,
          `---\ntitle: Tagged Page ${i}\ntopics: [tag-${i}]\n---\n\n# Tagged Page ${i}\n\nBody.\n`,
        );
      }

      const api = createViewerApi({ repoRoot: repo });
      const overview = await api.overview();

      expect(overview.topicNavigation).toEqual({ source: "tags", sidebarLimit: 8 });
      expect(overview.topics).toHaveLength(10);
      expect(overview.rootTopics).toHaveLength(8);
    });
  });

  it("returns job runs and parsed stream events", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "r");
      await scaffoldWiki(repo);
      const started = buildStartedJobRecord({
        jobId: "run_20260510120000_viewer",
        repoRoot: repo,
        startedAt: new Date("2026-05-10T12:00:00.000Z"),
        pid: process.pid,
        spec: {
          provider: { id: "codex", model: "gpt-5.5" },
          cwd: repo,
          prompt: "garden",
          metadata: {
            operation: "garden",
            targetKind: "wiki",
            targetPaths: ["src/viewer/api.ts"],
          },
        },
      });
      const finished = finishJobRecord({
        record: started,
        status: "done",
        finishedAt: new Date("2026-05-10T12:01:00.000Z"),
        providerSessionId: "session-123",
        summary: {
          created: 1,
          updated: 2,
          deleted: 0,
          usage: { totalTokens: 1234 },
        },
        pageChanges: {
          version: 1,
          jobId: started.id,
          created: ["new-page"],
          updated: ["viewer-jobs", "viewer-api"],
          deleted: [],
          description: "Updated viewer jobs.",
        },
      });
      await writeJobRecord(jobRecordPath(repo, finished.id), finished);
      await writeFile(
        jobLogPath(repo, finished.id),
        [
          JSON.stringify({
            timestamp: "2026-05-10T12:00:30.000Z",
            event: { type: "text_delta", content: "hello" },
          }),
          "not json",
          JSON.stringify({
            timestamp: "2026-05-10T12:00:31.000Z",
            event: {
              type: "tool_use",
              tool: "shell",
              display: { kind: "shell", command: "npm test", status: "started" },
            },
          }),
          "",
        ].join("\n"),
        "utf8",
      );

      const api = createViewerApi({ repoRoot: repo });
      const jobs = await api.jobs();
      expect(jobs.runs.map((run) => run.id)).toEqual([finished.id]);
      expect(jobs.runs[0]?.displayStatus).toBe("done");
      expect(jobs.runs[0]?.summary?.updated).toBe(2);
      expect(jobs.runs[0]?.pageChanges?.updated).toEqual([
        "viewer-jobs",
        "viewer-api",
      ]);
      expect(jobs.runs[0]?.displayTitle).toBe("Garden wiki");
      expect(jobs.runs[0]?.transcriptSource).toBeNull();

      const detail = await api.job(finished.id);
      expect(detail?.run.provider).toBe("codex");
      expect(detail?.run.model).toBe("gpt-5.5");
      expect(detail?.run.providerSessionId).toBe("session-123");
      expect(detail?.run.displaySubtitle).toBe("src/viewer/api.ts");
      expect(detail?.run.pageChangeDetails).toEqual({
        created: [{ slug: "new-page", title: null }],
        updated: [
          { slug: "viewer-jobs", title: null },
          { slug: "viewer-api", title: null },
        ],
        deleted: [],
      });
      expect(detail?.events).toHaveLength(3);
      expect(detail?.events[0]).toEqual({
        line: 1,
        timestamp: "2026-05-10T12:00:30.000Z",
        event: { type: "text_delta", content: "hello" },
      });
      expect(detail?.events[1]).toMatchObject({
        line: 2,
        invalid: true,
        raw: "not json",
      });
      expect(detail?.events[2]).toMatchObject({
        line: 3,
        timestamp: "2026-05-10T12:00:31.000Z",
        event: { type: "tool_use", tool: "shell" },
      });
      await expect(api.job("run_20260510120000_missing")).resolves.toBeNull();
    });
  });

  it("exposes transcript source separately from the provider that processed it", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "r");
      await scaffoldWiki(repo);
      const transcript = join(home, ".claude", "projects", "r", "session-1.jsonl");
      const started = buildStartedJobRecord({
        jobId: "run_20260510121000_session",
        repoRoot: repo,
        startedAt: new Date("2026-05-10T12:10:00.000Z"),
        pid: process.pid,
        spec: {
          provider: { id: "codex", model: "gpt-5.4" },
          cwd: repo,
          prompt: "absorb session",
          metadata: {
            operation: "absorb",
            targetKind: "session",
            targetPaths: [transcript],
          },
        },
      });
      await writeJobRecord(jobRecordPath(repo, started.id), started);
      await writeJobSpec(repo, started.id, {
        provider: { id: "codex", model: "gpt-5.4" },
        cwd: repo,
        prompt: [
          "Command context:",
          "- Command: sync",
          "- App: claude",
          "- Session id: session-1",
          `- Transcript: ${transcript}`,
        ].join("\n"),
        metadata: {
          operation: "absorb",
          targetKind: "session",
          targetPaths: [transcript],
        },
      });

      const api = createViewerApi({ repoRoot: repo });
      const jobs = await api.jobs();
      expect(jobs.runs[0]).toMatchObject({
        provider: "codex",
        model: "gpt-5.4",
        targetKind: "session",
        transcriptSource: "claude",
        displayTitle: "Absorb session transcript",
      });

      const detail = await api.job(started.id);
      expect(detail?.run.transcriptSource).toBe("claude");
    });
  });

  it("keeps job detail lookups inside the run store", async () => {
    await withTempHome(async (home) => {
      const repo = await makeRepo(home, "r");
      await scaffoldWiki(repo);
      const started = buildStartedJobRecord({
        jobId: "run_20260510120500_secure",
        repoRoot: repo,
        startedAt: new Date("2026-05-10T12:05:00.000Z"),
        pid: process.pid,
        spec: {
          provider: { id: "claude" },
          cwd: repo,
          prompt: "absorb",
          metadata: { operation: "absorb" },
        },
      });
      const leakedLogPath = join(home, "outside-log.jsonl");
      await writeFile(
        leakedLogPath,
        `${JSON.stringify({
          timestamp: "2026-05-10T12:05:01.000Z",
          event: { type: "text", content: "outside file" },
        })}\n`,
        "utf8",
      );
      await writeJobRecord(jobRecordPath(repo, started.id), {
        ...started,
        logPath: leakedLogPath,
      });

      const api = createViewerApi({ repoRoot: repo });

      await expect(api.job("../run_20260510120500_secure")).resolves.toBeNull();
      const detail = await api.job(started.id);
      expect(detail?.events).toEqual([]);
      expect(detail?.run.displaySubtitle).toBeNull();
    });
  });
});
