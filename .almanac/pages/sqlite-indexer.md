---
title: SQLite Indexer
summary: >-
  The SQLite indexer powers query commands but inherits `better-sqlite3` native-binding
  failures and generated-index schema drift.
topics:
  - systems
  - storage
sources:
  - id: source-architecture-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/30/rollout-2026-05-30T18-19-49-019e7b2f-c7d8-7640-a485-6de2f5a4a62f.jsonl
    note: >-
      Records the correction that page `sources:` parsing is markdown projection work and that the
      legacy source-frontmatter rewriter belongs to health rather than a generic sources subsystem.
  - id: search-query-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/06/07/rollout-2026-06-07T17-38-44-019ea4aa-e76e-7841-94a0-b00f3c24ccf8.jsonl
    note: >-
      Records the 2026-06-08 conclusion that search/query does not need a major rewrite yet, but
      should split filter builders when new query features land.
  - id: design-studio-branch-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/06/09/rollout-2026-06-09T16-03-59-019eaea0-e2b1-7b93-b4ca-64145266ae12.jsonl
    note: >-
      Records a required wiki lookup during a design-studio branch inspection failing because
      the local `better-sqlite3` binding could not load.
  - id: reindex-command
    type: file
    path: src/cli/commands/reindex.ts
    note: Shows that explicit `almanac reindex` calls `runIndexer()` and reports its result.
  - id: indexer-fast-path
    type: file
    path: src/wiki/indexer/index.ts
    note: Shows that `runIndexer()` skips rows whose `content_hash` and `file_path` already match.
  - id: register-query-commands
    type: file
    path: src/cli/register-query-commands.ts
    note: Migrated from legacy files.
  - id: search
    type: file
    path: src/cli/commands/search.ts
    note: Migrated from legacy files.
  - id: show
    type: file
    path: src/cli/commands/show.ts
    note: Migrated from legacy files.
  - id: index
    type: file
    path: src/cli/commands/health/index.ts
    note: Migrated from legacy files.
  - id: schema
    type: file
    path: src/wiki/indexer/schema.ts
    note: Migrated from legacy files.
  - id: index-2
    type: file
    path: src/wiki/indexer/index.ts
    note: Migrated from legacy files.
  - id: frontmatter
    type: file
    path: src/wiki/indexer/frontmatter.ts
    note: Migrated from legacy files.
  - id: page-sources
    type: file
    path: src/wiki/indexer/page-sources.ts
    note: Migrated from legacy files.
  - id: wikilinks
    type: file
    path: src/wiki/indexer/wikilinks.ts
    note: Migrated from legacy files.
  - id: paths
    type: file
    path: src/wiki/indexer/paths.ts
    note: Migrated from legacy files.
  - id: resolve-wiki
    type: file
    path: src/wiki/indexer/resolve-wiki.ts
    note: Migrated from legacy files.
  - id: duration
    type: file
    path: src/wiki/indexer/duration.ts
    note: Migrated from legacy files.
  - id: query-search
    type: file
    path: src/wiki/query/search.ts
    note: Executes the search SQL plan and hydrates result topics.
  - id: query-search-plan
    type: file
    path: src/wiki/query/search-plan.ts
    note: Builds the current FTS/list SQL plan and shared search filters.
  - id: query-file-mentions
    type: file
    path: src/wiki/query/file-mentions.ts
    note: Builds file and folder mention filters for search.
  - id: index-3
    type: file
    path: src/wiki/health/index.ts
    note: Migrated from legacy files.
  - id: maintenance
    type: file
    path: src/wiki/sources/maintenance.ts
    note: Migrated from legacy files.
  - id: abi-guard
    type: file
    path: src/abi-guard.ts
    note: Migrated from legacy files.
  - id: cli
    type: file
    path: src/cli.ts
    note: Migrated from legacy files.
  - >-
    /Users/kushagrachitkara/.codex/sessions/2026/05/11/rollout-2026-05-11T14-32-08-019e18f4-5e73-7790-ba49-73cc02544a58.jsonl
  - >-
    /Users/rohan/.codex/sessions/2026/05/15/rollout-2026-05-15T01-43-21-019e2a29-293a-7263-b6ce-0a9dc0af792a.jsonl
verified: 2026-05-15T00:00:00.000Z

---

# SQLite Indexer

The indexer (`src/wiki/indexer/`) builds and maintains `.almanac/index.db` — a SQLite database that powers all query commands (`search`, `show`, `health`, `topics show`). It runs silently before every query command. Freshness checks compare page and topic-file mtimes against the database mtime; once a reindex starts, unchanged page rows are skipped by `content_hash` and `file_path`.

## Query output contract

Query commands should stay quiet by default and reserve richer context for explicit flags. `almanac search` defaults to one slug per line even in a TTY; `--verbose` and the older `--summaries` flag print one-line summaries. `almanac show <slug>` defaults to the page body only; `--verbose` restores the metadata header, separator, and body view. Field flags such as `--title`, `--topics`, `--files`, and JSON output keep their existing explicit shapes.

`almanac search` should remain a wiki-page search by default. A 2026-05-15 product/API discussion rejected mixing real source files into the default result stream because it would blur Almanac's contract with ordinary code search tools such as `rg` and make slug piping less predictable. A future explicit mode such as `almanac search --files "query"` is consistent with the model if it returns file refs attached to matching wiki pages; that mode should mean "show the source files the wiki says matter for this concept," not "grep the repository too." `almanac show <slug> --files` and `almanac search --mentions <path>` remain the direct file-aware surfaces for one page or one source path.

The current search-query architecture is intentionally modest. `[[src/wiki/query/search.ts]]` asks `[[src/wiki/query/search-plan.ts]]` for SQL and params, executes the plan, and hydrates each result with topics. `search-plan.ts` still assembles archive, topic, mention, freshness, orphan, FTS, and list-mode clauses in one builder, while `[[src/wiki/query/file-mentions.ts]]` owns the file/folder mention filter. That shape is acceptable because the current query surface is small; the project should split filter builders and topic hydration only when new behavior such as source filtering, snippets, OR groups, topic descendants, semantic/vector search, more ranking modes, or reusable viewer/API search plans makes the combined builder materially harder to maintain. [@query-search] [@query-search-plan] [@query-file-mentions] [@search-query-session]

## Schema

Defined in `src/wiki/indexer/schema.ts` and applied idempotently on every open (`CREATE ... IF NOT EXISTS`). Tables:

- `pages` — one row per `.md` file: `slug`, `title`, `summary`, `file_path`, `content_hash`, `updated_at`, `archived_at`, `superseded_by`
- `topics` — topic metadata (slug, title, description); populated from `topics.yaml` at reindex time
- `page_topics` — page↔topic many-to-many; FK cascade-deletes on page removal
- `topic_parents` — DAG edges; has a `CHECK (child_slug != parent_slug)` constraint
- `file_refs` — parsed file/folder links; stores both `path` (lowercased, for GLOB queries) and `original_path` (as-written, for display and case-sensitive dead-ref checks)
- `wikilinks` — page-slug links
- `cross_wiki_links` — cross-wiki links
- `fts_pages` — FTS5 virtual table (slug + title + content); **ON DELETE CASCADE does NOT apply to FTS5 virtual tables**; the indexer must issue an explicit `DELETE FROM fts_pages WHERE slug = ?` before re-inserting a changed page row, or the old content remains searchable alongside the new content

## Markdown Projection Boundary

`src/wiki/indexer/` owns the pipeline that turns markdown pages into queryable rows. That includes frontmatter parsing in `[[src/wiki/indexer/frontmatter.ts]]`, source normalization in `[[src/wiki/indexer/page-sources.ts]]`, wikilink extraction, path normalization, and the `file_refs` and `page_sources` projections in SQLite. `[[src/wiki/health/index.ts]]` owns the health checks that query those projections.

The 2026-05-30 source-architecture discussion rejected a separate `provenance/`, `page-metadata/`, or generic source-connector owner for page-source projection code at the current stage. Page `sources:` are provenance in the document model, but the code that parses, indexes, checks, and displays them is indexer-facing markdown projection infrastructure. The deterministic rewrite helper now lives in `[[src/wiki/sources/maintenance.ts]]` because `almanac migrate legacy-sources` owns mechanical source-frontmatter migration; it should not become a source-connector module or a generic provenance subsystem. [@source-architecture-session]

## Schema versioning

`SCHEMA_VERSION` constant (currently `4`). On open, if `user_version < SCHEMA_VERSION`, affected tables are dropped or altered and the hash column is cleared to force a full reindex. The v3 migration adds `pages.summary` with `ALTER TABLE`; the other current migrations rebuild changed projection tables from markdown.

## Path handling

All stored paths are lowercase + forward-slashes + no `./` prefix (normalized at write and query time). `GLOB` is used for path queries, never `LIKE` — `LIKE` treats `_` as a wildcard, and Next.js-style paths like `src/[id]/page.tsx` contain GLOB metacharacters that must be escaped. See [[wikilink-syntax]] for the link classification rules that feed `file_refs`.

## Freshness

`better-sqlite3` is the synchronous SQLite driver. WAL journal mode is set on first open and persists in the DB header.

`almanac reindex` runs the indexer even when the freshness check would skip work, but the current command path does not clear `pages.content_hash`. A page whose `content_hash` and `file_path` already match the existing row is skipped inside `runIndexer()`. That means parser, projection, or source-normalization changes can require deleting the generated `.almanac/index.db` or triggering a schema-version rebuild before old derived rows such as `page_sources` are recomputed. [@reindex-command] [@indexer-fast-path]

Schema freshness is version-number based rather than shape-based. `isIndexSchemaStale()` returns true only when `PRAGMA user_version` is lower than `SCHEMA_VERSION`, and `openIndex()` only runs migrations in that same lower-version case. A generated `.almanac/index.db` with an equal or higher `user_version` but missing columns can therefore bypass migration because `CREATE TABLE IF NOT EXISTS pages` does not add columns to an existing table. If query commands fail with a missing-column SQL error such as `pages has no column named archived_at`, delete `.almanac/index.db`; the markdown pages and `topics.yaml` are the source of truth. [@schema]

## Native binding constraint

The query stack still inherits `better-sqlite3`'s old-ABI native binding behavior: a global or local install can work on one Node version and then fail after an `nvm`/Volta/FNM switch until the package is rebuilt for the new runtime.

Installed package bins now mitigate that by routing through [[install-time-node-launcher]]. The launcher records the installing Node executable during `postinstall` and respawns `dist/codealmanac.js` with that same binary later, which keeps normal `almanac` invocations from drifting onto a different ABI through ambient `PATH`.

`src/abi-guard.ts` still exists because the launcher is not a complete replacement for repair guidance. Direct entrypoint calls such as `node dist/codealmanac.js ...`, missing `install-runtime.json`, or a deleted pinned Node executable can still surface the old mismatch class. In those cases the guard fails fast with a rebuild hint instead of surfacing a later opaque `require()` crash.

This constraint explains one CLI boundary elsewhere in the repo: [[lifecycle-cli]] routes `setup` and `automation install|status|uninstall` through a sqlite-free fast path in `src/cli.ts`, so basic onboarding and scheduler repair still work even when the query/index stack cannot load `better-sqlite3`.

[[almanac-doctor]] surfaces the same failure mode as structured install state: `install.sqlite` reports whether the binding loads and prints the rebuild hint as a `run:` fix string. The launcher reduces how often users reach that state, but doctor still owns the diagnosis when they do.

It also creates one absorb-time workflow fallback that is easy to forget: if a local or global `almanac search`/`show` command fails because the installed `better-sqlite3` binary targets the wrong Node ABI, the checked-in wiki pages under `[[.almanac/pages/]]` are still readable as plain files. Future agents should treat that as the immediate fallback for wiki context gathering instead of assuming the wiki itself is unavailable.
