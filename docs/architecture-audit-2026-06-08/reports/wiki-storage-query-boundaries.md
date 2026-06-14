# Wiki Storage / Query Boundary Audit

Repo root: `/Users/rohan/Desktop/Projects/codealmanac`

Scope: `src/wiki`, `src/viewer`, and CLI command boundaries for `search`, `show`, `tag`, `source`, `health`, `topics`, and `list`.

Read first:

- `MANUAL.md`
- `.almanac/README.md`
- `almanac show sqlite-indexer`
- `almanac show wikilink-syntax`
- `almanac show almanac-serve`
- `almanac show wiki-organization-primitives`
- `almanac show documenting-software-architectures`
- `almanac show accidental-special-case-architecture`
- `.claude/agents/review.md`

No source code was modified during this audit.

## Overall Take

The storage/indexer core is mostly coherent. `src/wiki/indexer/` owns markdown-to-SQL projection, path normalization, source projection, wikilink classification, schema creation, and implicit freshness. That matches the wiki's intended architecture.

The weak boundary is the read/query layer. `src/wiki/query/` is too small for the amount of read projection the product now exposes. As a result, `src/cli/commands/search.ts`, `src/cli/commands/topics/*.ts`, and `src/viewer/api.ts` each assemble their own SQL result shapes. The viewer is also no longer just a wiki viewer; it has become a local console for global registry browsing, review decisions, connector status, and job observability.

The "pure query" invariant does not hold literally. It holds only if interpreted as: non-lifecycle commands do not invoke AI and do not write page prose. Query-looking commands still refresh `index.db`, may auto-register the repo in `~/.almanac/registry.json`, may read markdown bodies for `show` and viewer rendering, and some commands registered under query have explicit write modes.

## Findings

### 1. Restructure: The CLI Pure-Query Invariant Is Too Broad For The Code

`CLAUDE.md:97` says "The CLI never reads or writes page content" and that every other command operates on `index.db` and the filesystem. `MANUAL.md:149-150` says everything except `capture` and `bootstrap` is pure query/organization over SQLite.

The code contradicts the literal wording:

- `src/wiki/query/page-view.ts:122-125` reads the page markdown file to return body text.
- `src/cli/commands/show.ts:83-101` opens the index and calls `getPageView()`, so `almanac show` reads page content through the shared query helper.
- `src/viewer/api.ts:152-165` also calls `getPageView()`, so viewer page rendering reads markdown bodies.
- `src/wiki/health/index.ts:400-409`, `431-437`, `468-478`, `484-498`, and `544-570` read page files for source/citation and empty-page checks.
- `src/cli/register-query-commands.ts:169-178` registers `health --fix` under query commands, and `src/wiki/health/index.ts:96-105` can apply deterministic frontmatter fixes.
- `src/cli/register-query-commands.ts:202-209` registers `list --drop`, which writes the global registry through `src/cli/commands/list.ts:56-67`.
- Every query command in `src/cli/register-query-commands.ts:24-31`, `76-91`, `138-165`, `187-198`, and `212-217` can call `autoRegisterIfNeeded()`, which can write a registry entry at `src/wiki/registry/autoregister.ts:55-62`.

The behavior is mostly defensible. `show` cannot print a page body without reading markdown, implicit reindex is a documented derived-state write, and auto-registration is a stated registry policy. The problem is the invariant's wording. Future agents reading it can either over-restrict useful read behavior or miss the fact that "query" commands have allowed side effects.

Recommended shape:

- Restate the invariant as: "Only lifecycle operations invoke AI or write page prose. Read commands may refresh derived local index state and read committed markdown for display/validation. Organization commands may rewrite wiki metadata through explicit verbs such as `tag`, `topics`, `review`, and `health --fix`."
- Rename `registerQueryCommands()` or split it into `registerReadCommands()` and `registerRegistryCommands()` / `registerMaintenanceCommands()` so `serve`, `health --fix`, and `list --drop` are not hidden under a pure-query label.
- Keep `ensureFreshIndex()` as the common read-side entrypoint; the issue is the contract language, not the mechanism.

Why it matters: invariants teach future agents where exceptions are allowed, and the current wording is stricter than the product actually is.

### 2. Restructure: The Shared Query Layer Is Underpowered

`src/wiki/query/` currently has only:

- `src/wiki/query/search.ts` for FTS builders and file-mention normalization.
- `src/wiki/query/page-view.ts` for one full page projection.

Most actual read projections still live in command or viewer modules:

- `src/cli/commands/search.ts:96-255` builds archive, topic, mention, freshness, orphan, and FTS SQL directly.
- `src/cli/commands/search.ts:238-252` attaches topics in a second pass.
- `src/viewer/api.ts:330-352` defines `recentPagesSql()`, `pagesBySlugSql()`, and `pageSearchSql()`.
- `src/viewer/api.ts:355-370` defines `pageSummaries()` and attaches topics in its own second pass.
- `src/viewer/api.ts:438-464` rebuilds file-mention SQL and params from the same shared `buildFileMentionFilter()` primitive used by CLI search.
- `src/cli/commands/topics/read.ts:17-51` owns topic page-list SQL for the CLI.
- `src/viewer/api.ts:169-214` owns a separate topic detail projection for the viewer.
- `src/viewer/api.ts:406-436` owns topic summary SQL and parent attachment.
- `src/cli/commands/topics/list.ts:23-42` owns another topic summary/count projection.

Some divergence is intentional: CLI search uses token-prefix FTS (`src/cli/commands/search.ts:220-231`), while viewer submitted search uses quoted term FTS and suggestions use quoted prefix FTS (`src/viewer/api.ts:217-237`). That should stay explicit. The problem is that pagination, archive filtering, page description shape, topic attachment, file mention matching, and topic counts are not centralized.

Recommended shape:

- Add `src/wiki/query/pages.ts` with a `PagePreview` type, `recentPages()`, `pagesBySlug()`, `searchPages()`, and `pagesMentioningPath()`.
- Add `src/wiki/query/topics.ts` with `topicSummaryList()`, `topicDetail()`, `pagesDirectlyTagged()`, and `pagesForSubtree()`.
- Keep FTS query expression builders in `src/wiki/query/search.ts`, but have both CLI and viewer pass their chosen expression into shared page-query functions.
- Leave command files responsible for flags and text formatting only.
- Leave `src/viewer/api.ts` responsible for API payload assembly only.

Why it matters: viewer and CLI are already projecting the same graph differently, and the next schema or archive/filter change will need synchronized edits in several places.

### 3. Restructure: `src/viewer/api.ts` Is A Mixed Local Console, Not Just A Wiki API

The viewer page says `almanac serve` is a local read-only wiki viewer. The current API is broader:

- `src/viewer/api.ts:14-19` imports review-store concerns.
- `src/viewer/api.ts:22-28` imports job/run concerns.
- `src/viewer/api.ts:29-30` imports config and connector status.
- `src/viewer/api.ts:82-92` exposes `overview`, `page`, `topic`, `search`, `suggest`, `file`, `review`, `connections`, `jobs`, and `job` in one `ViewerApi`.
- `src/viewer/server.ts:124-142` routes `/review`, `/connections`, `/jobs`, and `/jobs/:runId` beside wiki graph routes.
- `src/viewer/global-api.ts:36-67` builds a global registry-backed viewer API over all registered wikis.
- `src/cli/commands/serve.ts:9-18` accepts `cwd` but does not use it; `startViewerServer()` creates a global API at `src/viewer/server.ts:22-28`.

This does not currently violate the no-AI rule or write page content. It does make the name "local read-only wiki viewer" less true. A user binding `--host` away from localhost is not just serving the current repo's wiki; they are exposing a registry-backed local console over reachable registered wikis and run records.

Recommended shape:

- Split `src/viewer/api.ts` into smaller APIs: `wiki-api.ts`, `jobs-api.ts`, `review-api.ts`, and `connections-api.ts`.
- Make `server.ts` compose those APIs at the routing layer.
- Decide whether `almanac serve` is "current wiki viewer" or "local Almanac console." If it is global, rename help text and docs accordingly. If it should be current-repo scoped, resolve and pass the repo root from `runServe()`.
- Consider warning when `--host` is not localhost, because the data exposed is broader than a single rendered wiki page.

Why it matters: the viewer's code shape now hides product scope decisions in one API file instead of making them explicit.

### 4. Fix: Health Owns Too Much Source/Markdown Cleanup Logic

`src/wiki/health/index.ts` is no longer only graph integrity checks. It also owns source citation checks and fix orchestration:

- The module comment at `src/wiki/health/index.ts:19-24` says health owns checks and deterministic repairs.
- `collectHealthReport()` assembles thirteen categories at `src/wiki/health/index.ts:76-90`.
- Source checks read and parse markdown repeatedly at `src/wiki/health/index.ts:328-498`.
- `citationsForFile()` contains the citation syntax regex at `src/wiki/health/index.ts:484-498`.
- Empty-page detection strips frontmatter with a local regex at `src/wiki/health/index.ts:550-552`, even though this module already imports `parseFrontmatter()`.
- `applyHealthFixes()` and `fixLegacySourceFrontmatter()` run writes at `src/wiki/health/index.ts:96-105` and `612-628`.
- The actual writer lives in `src/wiki/health/legacy-frontmatter-fix.ts:88-96`.

The current fix is bounded and documented: legacy `files:` / string `sources:` migration is deterministic and only exposed through `health --fix`. That exception is acceptable while it is the only repair. The issue is direction of travel. Health is becoming a report/fixer/source-parser module, and it already has duplicate frontmatter stripping.

Recommended shape:

- Move source/citation health helpers into `src/wiki/sources/health.ts` or `src/wiki/maintenance/source-frontmatter.ts`.
- Keep `src/wiki/health/index.ts` as the report composition layer.
- Reuse `parseFrontmatter(raw).body` or a shared frontmatter stripper for empty-page detection instead of a second regex.
- Keep `health --fix` explicitly narrow; do not let it become a general wiki-editing surface.

Why it matters: health is the place users trust for diagnosis, and bundling diagnosis, parsing, and repair makes future repair behavior easier to add casually.

### 5. Fix: Topic Read Queries Belong In `src/wiki/query`, Not CLI Command Files

Topic write ownership is reasonably clear. `src/wiki/topics/yaml.ts` owns `topics.yaml`, `src/wiki/topics/frontmatter-rewrite.ts` owns page-topic frontmatter rewrites, and mutating commands mostly sequence validation and writes.

Topic read ownership is less clear:

- `src/cli/commands/topics/read.ts:17-51` implements topic page-list SQL.
- `src/cli/commands/topics/show.ts:36-66` implements topic metadata, parent, and child queries.
- `src/cli/commands/topics/list.ts:23-42` implements topic list/count queries.
- `src/viewer/api.ts:169-214` implements a viewer topic detail projection.
- `src/viewer/api.ts:406-436` implements viewer topic summary and root-topic queries.
- `src/wiki/topics/dag.ts:62-90` is the only shared read primitive for descendants/subtree.

Recommended shape:

- Move topic list/detail/page-list projections into `src/wiki/query/topics.ts`.
- Keep `src/wiki/topics/` focused on topic storage, DAG mechanics, and frontmatter mutation.
- Keep `src/cli/commands/topics/*` focused on parsing options and formatting command output.

Why it matters: topic page counts and descendant behavior are a trust surface. The code already comments about count consistency in `src/cli/commands/topics/list.ts:28-32`; the same consistency should be enforced by shared code, not comments across modules.

### 6. Polish: Registry And Source Naming Have Residue

Registry storage is mostly clean, but two small residues are worth removing:

- `src/wiki/registry/index.ts:1-5` re-exports `toKebabCase` from the registry facade for compatibility, while production registry code imports from `src/slug.ts` directly. The only current use found is `test/registry.test.ts`.
- `src/wiki/registry/store.ts:116-121` defines `pathsEqual()`, while `src/wiki/registry/autoregister.ts:108-118` duplicates the same logic as `samePath()` with a comment explaining the duplication.

The duplication is small, but path equality is a registry invariant. Keeping it private in two files is more brittle than exporting a small internal helper such as `src/wiki/registry/path-equality.ts`.

The term `source` is also overloaded:

- Frontmatter has `sources:` and the index has `page_sources` (`src/wiki/indexer/schema.ts:71-83`).
- Ingest has source refs (`src/ingest/source-ref.ts`).
- The CLI has `almanac source github issue|pr` registered at `src/cli/register-setup-commands.ts:139-184`.

The command is not wrong, but "source" now means evidence, external object, and ingest target depending on context. `external-source`, `connector-source`, or `github-source` would be clearer if this surface grows.

Why it matters: these are small examples of compatibility and naming drift. They are not urgent, but they teach future contributors that local exceptions are acceptable.

## Boundary Answers

### Does The CLI Pure-Query Invariant Hold?

No, not literally. Query-looking commands can refresh `index.db`, auto-register the current repo, read page markdown bodies, and in explicit modes mutate metadata or registry state. The stronger invariant should be narrowed to "no AI and no page-prose writes outside lifecycle operations; deterministic metadata organization is explicit."

### Are Storage, Query, And Domain Responsibilities Clear?

Partially. `src/wiki/indexer/` and `src/wiki/registry/` are understandable. `src/wiki/topics/` is clear on writes but incomplete on read projections. `src/wiki/query/` is underdeveloped, so query/domain knowledge leaks into CLI and viewer code.

### Does Viewer Code Duplicate Query Projections?

Yes. `src/viewer/api.ts` duplicates page description, FTS result, file mention, topic summary, and topic detail SQL that should live under `src/wiki/query/`.

### Does Health Have Cleanup Logic That Belongs Elsewhere?

Yes, but it is currently bounded. The legacy-source fixer can stay as a narrow exception, but the source/citation health checks and fix orchestration deserve their own maintenance/source module before more repairs accrete.

### Is Naming Simple Or Muddy?

Mostly simple in the indexer and topics storage code. Muddy areas are `query` as a command grouping, `viewer` as a global local console, and `source` as evidence/ingest/external-object terminology.

## Recommended Refactor Sequence

1. Clarify the invariant in `CLAUDE.md` / `MANUAL.md`: separate read commands, organization commands, lifecycle AI commands, derived-state writes, and page-prose writes.
2. Extract shared page and topic read projections into `src/wiki/query/pages.ts` and `src/wiki/query/topics.ts`.
3. Split `src/viewer/api.ts` into wiki, jobs, review, and connections APIs, with `server.ts` composing routes.
4. Move source/citation health helpers and the legacy frontmatter fixer out of `src/wiki/health/index.ts` into a source-maintenance module.
5. Remove the registry `toKebabCase` compatibility re-export after tests move, and centralize path equality inside registry internals.

