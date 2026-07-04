---
title: almanac serve (Local Viewer)
summary: >-
  `almanac serve` is a local read-only viewer over wiki pages, the SQLite index, run records, and
  review escalations.
topics:
  - cli
  - decisions
  - systems
status: active
verified: 2026-05-31T00:00:00.000Z
sources:
  - id: front-door-cleanup
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/28/rollout-2026-05-28T12-14-55-019e6f94-fae1-7780-b2c9-3e2f3d6b6f3e.jsonl
    note: Records the cleanup that removed project-overview as a viewer featured-page fallback.
  - id: source-rail
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/28/rollout-2026-05-28T12-14-55-019e6f94-fae1-7780-b2c9-3e2f3d6b6f3e.jsonl
    note: >-
      Records the source-provenance implementation that added source records to the page view and
      viewer rail.
  - id: review-escalations-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/28/rollout-2026-05-28T12-14-55-019e6f94-fae1-7780-b2c9-3e2f3d6b6f3e.jsonl
    note: Records the review escalation CLI and the follow-up serve UI route.
  - id: serve-command-registration
    type: file
    path: src/cli/register-query-commands.ts
    note: Defines the `almanac serve` host and port options and their defaults.
  - id: serve-runtime
    type: file
    path: src/cli/commands/serve.ts
    note: Prints the viewer URL and keeps the local server running until interrupt.
  - id: brand-direction-session
    type: conversation
    path: /Users/kushagrachitkara/.codex/sessions/2026/06/04/rollout-2026-06-04T21-40-03-019e9366-1b93-7be3-bf26-f15c447068bd.jsonl
    note: Records the later brand exploration that preferred a celestial moon-and-instrument mark over the older centered-monogram and open-book directions.
  - id: serve
    type: file
    path: src/cli/commands/serve.ts
    note: Migrated from legacy files.
  - id: api
    type: file
    path: src/viewer/api.ts
    note: Migrated from legacy files.
  - id: runs
    type: file
    path: src/codealmanac/wiki/viewer/runs.py
    note: Projects lifecycle run records and log events into viewer DTOs.
  - id: server
    type: file
    path: src/viewer/server.ts
    note: Migrated from legacy files.
  - id: static
    type: file
    path: src/viewer/static.ts
    note: Migrated from legacy files.
  - id: page-view
    type: file
    path: src/wiki/query/page-view.ts
    note: Migrated from legacy files.
  - id: search
    type: file
    path: src/wiki/query/search.ts
    note: Migrated from legacy files.
  - id: index
    type: file
    path: viewer/index.html
    note: Migrated from legacy files.
  - id: almanac-logo
    type: file
    path: viewer/almanac-logo.png
    note: Migrated from legacy files.
  - id: app
    type: file
    path: viewer/app.js
    note: Migrated from legacy files.
  - id: app-2
    type: file
    path: viewer/app.css
    note: Migrated from legacy files.
  - id: routes
    type: file
    path: viewer/routes.js
    note: Migrated from legacy files.
  - id: runs-view
    type: file
    path: src/codealmanac/api/assets/viewer/runs.js
    note: Renders lifecycle run list, detail, event logs, and polling in the static viewer.
  - id: viewer-routes
    type: file
    path: src/codealmanac/api/assets/viewer/routes.js
    note: Defines `#/runs` and `#/runs/<run-id>` routes.
  - id: search-suggestions
    type: file
    path: viewer/search-suggestions.js
    note: Migrated from legacy files.
  - id: serve-command-test
    type: file
    path: test/serve-command.test.ts
    note: Migrated from legacy files.
  - id: viewer-api-test
    type: file
    path: test/viewer-api.test.ts
    note: Migrated from legacy files.
  - id: viewer-ui-assets-test
    type: file
    path: test/viewer-ui-assets.test.ts
    note: Migrated from legacy files.
  - docs/plans/2026-05-10-local-viewer.md
  - docs/plans/2026-05-10-viewer-jobs-dashboard.md
  - docs/plans/2026-05-11-jobs-stream-ui-garden.md
  - ../openalmanac/frontend/src/components/wiki/wiki-theme.css
  - ../openalmanac/frontend/src/components/wiki/wiki-chrome.css
  - ../openalmanac/frontend/src/components/wiki/vintage-prose.css
  - ../openalmanac/frontend/src/components/wiki/layout/WikiLayout.tsx
  - ../usealmanac/index.html
  - ../usealmanac/logo1.png

---

# almanac serve (Local Viewer)

`almanac serve` is a lightweight local read-only web viewer for browsing a repo's Almanac wiki. It is the preferred "read the wiki" experience for humans; filesystem browsing is the fallback and editor interface, not the primary UX. Designed and implemented 2026-05-10.

The viewer is mostly a read-only client over existing wiki/index/run-record primitives. `[[src/codealmanac/wiki/index/]]` owns the SQLite-backed index that search, show, health, topics, and the viewer read.

## Rationale

A wiki graph is awkward to inspect as files. You want backlinks, topic pages, file references, archive state, search, and "what should I read next?" rendered and linked, not raw markdown in a file tree. A folder tree cannot show this well.

The answer is a local viewer rather than a cloud app, hosted service, or complex editing tool. Markdown stays the source of truth; the viewer is disposable.

## Invocation

Run the installed CLI from a repo that contains `.almanac/`:

```bash
almanac serve
```

By default the command binds `127.0.0.1:3927`; `src/cli/commands/serve.ts` prints the exact URL as `almanac viewer: <url>` before waiting for Ctrl+C. [@serve-command-registration] [@serve-runtime]

Use `--port <n>` when the default port is busy, and use `--host <host>` only when the viewer needs to bind somewhere other than localhost. [@serve-command-registration]

```bash
almanac serve --port 4320
```

From a source checkout, build first and run the compiled local binary when testing uninstalled viewer changes:

```bash
npm run build
node dist/codealmanac.js serve
```

The viewer reads `.almanac/pages/*.md` and `.almanac/index.db`. It triggers an implicit reindex (same as other query commands) so the index is fresh.

## Routes

```text
/                          overview / wiki homepage
/page/:slug                rendered page with backlinks sidebar
/topic/:slug               topic + descendant pages list
/search?q=...              FTS search results
/file?path=src/foo.ts      pages mentioning a file
/runs                      runs dashboard — list of recent lifecycle runs
/runs/:runId               run detail — status and event timeline
```

The left-rail search box uses `/api/suggest` while typing, then `/search?q=...` for submitted searches. Suggestions are bounded to the top eight pages and reuse the same FTS path as search.

The page rail is hidden for run routes — these views use a dedicated full-width layout rather than the three-panel wiki layout.

The home route treats `.almanac/pages/getting-started.md` as the single markdown-backed front door. `project-overview.md` is no longer a featured fallback in the viewer API or frontend; it can still be read as a normal page if a wiki has one.

The review route reads `.almanac/review.yaml` through the viewer API and groups items by `open`, `decided`, and `applied`. It is a decision inbox, not a generic issue tracker: open items are unresolved source conflicts, decided items are ready for Garden to apply, and applied items are audit history.

## What the viewer provides

- Page reading with rendered markdown
- Wikilinks clickable (navigate within viewer)
- Full-text search
- Instant page suggestions in the left-rail search box
- Topic browser
- Backlinks panel per page
- File reference listings (pages mentioning a given source file)
- Source listings in the page rail, with file sources linked to `/file` views and web sources linked externally
- Archive / superseded indicators
- Runs dashboard with run list and detail/event view
- Graph sidebar (deferred)
- Review inbox for human decisions on unresolved conflicts raised by lifecycle agents

## What the viewer does not do

- No authentication
- No cloud sync or remote access
- No editing UI (markdown stays in editor/filesystem)
- No AI calls
- No database writes (except implicit reindex)
- No separate content model

## Packaging architecture

The viewer is a small static bundle shipped inside the npm package. The CLI serves it directly from the package install path via `src/viewer/static.ts`, which walks up from `__dirname` to find the package root and reads `viewer/*.{html,js,css}` directly. No separate `npm install` step.

```text
codealmanac package:
  viewer/
    index.html           # links app.css and app.js
    app.css              # served CSS: --ca-* tokens, wiki layout
    app.js               # router and chrome glue; wiki views inline
    routes.js            # wiki route helpers and wikilink route classification
    runs.js              # runs dashboard, detail view, event rendering, and polling
    search-suggestions.js # debounced left-rail search suggestions

almanac serve:
  Node http.createServer (no Express)
  serves viewer/ as static assets
  JSON API backed by index.db + markdown files
```

Next.js was explicitly rejected as too heavy. Express was not added; Node's `http` module is sufficient for a local read-only viewer. React and Preact were not used; the frontend is vanilla JS with a thin `h()` helper (inline in `viewer/app.js`) for building DOM nodes without a framework.

## Source module structure

The viewer is a read-only client over the same persisted index and run-record source files that the CLI uses. It should not introduce a separate database model or forked parser. Shared query mechanics live under `[[src/codealmanac/wiki/index/]]` rather than in viewer-specific helpers.

Actual source layout:

```text
src/
  commands/
    serve.ts          # thin CLI wrapper: resolve wiki root, start server, wait for Ctrl+C

  viewer/
    api.ts            # createViewerApi(): overview(), page(), topic(), search(), suggest(), file(), runs(), run()
    run-types.ts      # shared viewer run response shapes
    runs.ts           # runs API logic: listViewerRuns(), getViewerRun(), storage access, run-id safety
    server.ts         # startViewerServer(): HTTP routing for /api/* and static assets
    static.ts         # readViewerAsset() / readViewerIndex(): serves viewer/ from package root

  query/
    page-view.ts      # getPageView(db, slug) → PageView; shared by show command and viewer API
    search.ts         # shared FTS query builders and file-reference matching primitives

viewer/               # bundled static frontend (no build step required at runtime)
  index.html
  app.js              # router and chrome glue; wiki views (home, page, topic, search, file) inline
  routes.js           # shared route helpers for wiki-scoped URLs and wikilinks
  app.css             # all wiki tokens and layout CSS
  runs.js             # runs list, run detail, event rendering, and polling
  search-suggestions.js # left-rail search suggestion controller
```

The current Python implementation serves HTTP from `src/codealmanac/api/routes.py`. `ViewerService` owns wiki-API payload assembly and delegates run projection to `src/codealmanac/wiki/viewer/runs.py`. `RunLedgerService` owns run storage access, run-id validation, and event reads through `src/codealmanac/runs/ledger/`. The static frontend in `src/codealmanac/api/assets/viewer/` is plain HTML plus vanilla JS; `main.js` handles routing and wiki views, and `runs.js` handles run list/detail rendering and polling.

The viewer does not duplicate run storage rules or introduce its own run model.

## Key API types

`ViewerService` exposes `overview()`, `page(slug)`, `topic(slug)`, `search(query)`, `file(path)`, `runs()`, and `run(runId)`. The HTTP API maps those reads to `/api/overview`, `/api/page/{slug}`, `/api/topic/{slug}`, `/api/search`, `/api/file`, `/api/runs`, and `/api/runs/{run_id}`.

`search()` and `suggest()` use different FTS query builders from `[[src/wiki/query/search.ts]]`. `search()` calls `buildQuotedTermFtsQuery()`, which wraps each whitespace-split term in exact-phrase quotes (`"term"`) and ANDs them — suitable for complete submitted queries. `suggest()` calls `buildQuotedPrefixFtsQuery()`, which appends `*` to each quoted term (`"term"*`) — FTS5 prefix matching that returns results while the user is still typing. Using the submitted-query builder for suggest would break as-you-type completion because incomplete words would not match their eventual full form.

`PageView` is defined in `src/wiki/query/page-view.ts` and includes: slug, title, summary, file\_path, updated\_at, archived\_at, superseded\_by, supersedes, topics, file\_refs, source records, wikilinks\_out, wikilinks\_in, cross\_wiki\_links, and body (raw markdown). When returned by the viewer API `page()` method, a `related_pages` field is appended — page summaries for all wikilinks\_in, wikilinks\_out, and supersedes/superseded\_by targets, deduplicated, for the frontend to render titles without extra fetches.

`overview()` returns `featuredPages.gettingStarted` when the wiki contains `getting-started.md`. It does not return `featuredPages.projectOverview`; the 2026-05-28 front-door cleanup made `getting-started.md` the only special homepage convention.

`ViewerRunRecord` is the projected run row. It carries `run_id`, `kind`, `status`, title, summary, error, timestamps, log path, page changes, and optional harness transcript metadata. `ViewerRun` returns one projected run plus `ViewerRunEvent[]`, where each event carries sequence, timestamp, kind, message, and an optional normalized harness event.

## Runs Dashboard UI

The runs dashboard (`#/runs`) lists lifecycle run records in reverse-chronological order. Each row shows the run title, summary or error, status, kind, and last update time. Clicking any row navigates to `#/runs/<run-id>`.

The run detail view (`#/runs/<run-id>`) renders run facts followed by an event log:

- **Run panel**: run id, status, kind, update timestamp, log path, optional harness transcript, summary, and error.
- **Event log**: sequence, event kind, timestamp, message, and structured harness details when present.

The desired run detail hierarchy is outcome-first, not colophon-first. The first screen should answer whether the run succeeded, what kind of run it was, what pages were created or modified, what input transcript/file/folder the run ingested, and whether that input can be opened for inspection. Started and finished timestamps are useful but secondary.

The run overview uses a compact dashboard hierarchy rather than a hero plus scattered facts. The title and subtitle stand alone, then a metric grid answers status, time taken, model, and usage as separate cards. Status cards use a colored state treatment so completion, active work, and failures are visually distinct. Outcome cards below handle page changes and source/ingested transcript details. Run details stays collapsed for audit fields such as exact timestamps, session ids, and log paths.

`runs.js` renders structured event details directly from the `ViewerRunEvent` payloads. The current Python viewer does not have a separate transcript-projection module.

Polling behavior: while status is `queued` or `running`, the list and detail views schedule a re-fetch every 1.5 seconds via `runs.js`. On re-render, any existing poll timer is cancelled before scheduling a new one. Polling stops automatically when the route changes or the status reaches a terminal state.

The poll timer is private state inside `runs.js`. Route changes call `clearRunPolling()` from `main.js`, keeping the global router aware of cleanup without storing run-specific state in the main viewer shell.

## UI direction

The frontend uses the `usealmanac.com` brand direction: warm paper surfaces, Palatino-style serif reading typography, supporting sans/mono stacks that match the landing page, and botanical green accents. Color tokens live in `viewer/app.css` under the `--ca-*` namespace:

```css
--ca-bg: #faf6ed;
--ca-surface: #f4efe4;
--ca-surface-deep: #ede5d2;
--ca-paper: #fffaf0;
--ca-border: #d8d0c0;
--ca-text: #342f25;
--ca-muted: #695f50;
--ca-accent: #166534;
--ca-accent-hover: #15803d;
--ca-accent-bright: #16a34a;
--ca-serif: "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
--ca-sans: "DM Sans", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--ca-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
```

The accent color was revised from OpenAlmanac navy (`#1a3a5c`) to the usealmanac green (`#166534`) on 2026-05-12 so the local viewer matches the public landing page. A 2026-05-15 attempt to switch the viewer to a brighter OpenAlmanac-inspired blue (`#255f8f`) was reverted at user request, so green remains the active viewer direction. The active token namespace is `--ca-*` in `viewer/app.css`.

The brand mark is the usealmanac open-book logo at `viewer/almanac-logo.png`. The left rail subtitle is `Agent-maintained knowledge`, matching the landing-page eyebrow. A later June 2026 brand exploration preferred the more minimal celestial mark described in [[almanac-brand-direction]], but those assets have not been applied to the viewer yet. [@brand-direction-session]

Three-panel layout (desktop):

```text
Left rail        Main reader              Right rail
-----------      ------------------       ----------
Search           Rendered page            Backlinks
Topics list      (wikilinks clickable)    File refs
Recent pages
```

The left rail handles navigation and search. The main reader renders markdown (headings, paragraphs, lists, code blocks, inline code, wikilinks). The right rail shows backlinks, file references, and page sources. File sources route to the viewer's `/file` page, web sources open externally, and non-file/non-web source types render as source rows without navigation. Wikilinks in the reader navigate within the viewer via client-side routing.

The overview topic statistic counts every indexed topic. The topic filter strip shows top-level/root topics only and labels itself as such; when nested topics exist outside the strip, the strip shows the nested-topic count so the totals do not appear contradictory.

Hero-style mono eyebrow labels are not part of the current viewer direction. The page title and supporting summary should carry the section identity without a `// LABEL` line above the heading.

The library route should use direct product copy. Avoid poetic phrases such as "field guide" or "written in the margins"; the page should state that it lists registered wikis on the machine and should show global wikis/pages/topics counts as large dashboard stats rather than as a small mono strip.

## Relationship to filesystem layout

The viewer is the reason a full two-level docs tree is not needed. Because the viewer handles navigation, topic browsing, and backlinks, curated hub pages can stay inside `.almanac/pages/` instead of becoming a complete parallel hierarchy.

The viewer still reads from `.almanac/pages/` — the migration to a visible `almanac/` directory discussed in [[wiki-organization-primitives]] has not been implemented as of 2026-05-10 and is a breaking spec change that would need a migration command.

## Testing

`test/serve-command.test.ts` starts the server at port 0 (OS-assigned), verifies the static HTML is served, confirms `/api/overview` returns correct page counts, and checks `/api/page/:slug` returns title and body.

`tests/test_viewer_service.py` tests `ViewerService` in isolation: seeds a repo with linked pages, verifies overview, page, topic, search, file, runs, and run detail behavior.

`tests/test_api.py` checks that the served static assets include expected strings for the runs nav item, runs module, polling, and structured harness details. This guards the HTML/JS/CSS bundle against accidental deletion of feature-critical strings.
