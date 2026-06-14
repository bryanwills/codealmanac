# Source Map

## Layout And Root Detection

- `src/wiki/locations.ts` defines runtime, canonical docs, legacy pages, index,
  review, and topics paths.
- `src/paths.ts` still owns repo-root discovery and now recognizes both runtime
  `.almanac/` and tracked `docs/almanac/` markers.
- `src/wiki/indexer/resolve-wiki.ts` resolves CLI query roots and registered
  wiki reachability.
- `src/wiki/registry/autoregister.ts` uses root discovery to register repos.

## Indexing And Snapshots

- `src/wiki/indexer/index.ts` reads all `wikiPageRoots()`, prefers
  `page_id` over filename, and gives canonical docs pages precedence over
  legacy pages.
- `src/jobs/snapshots.ts` and `src/jobs/wiki-effects.ts` snapshot canonical and
  legacy page roots for lifecycle jobs.
- `src/wiki/indexer/frontmatter.ts` parses `page_id`.

## Topics

- `src/wiki/locations.ts` exposes topic-file resolution for indexing.
- `src/wiki/topics/paths.ts` chooses the mutable topic file path for
  deterministic topic commands.
- `src/wiki/indexer/topics-yaml.ts` applies topic metadata into SQLite.
- `docs/almanac/topics.yaml` is the canonical CodeAlmanac topic file and now
  preserves legacy topic neighborhoods.

## Operations And Prompts

- `src/operations/run.ts` injects runtime path context and auto-commit scope.
- `src/operations/build.ts` counts existing pages across wiki roots.
- `src/operations/garden.ts` targets `docs/almanac/` and
  `.almanac/review.yaml`.
- `prompts/base/*.md` and `prompts/operations/*.md` define the new
  human-readable docs/wiki contract.

## Viewer And Setup

- `src/viewer/api.ts` exposes `featuredPages.frontDoor` and preserves
  `gettingStarted` fallback.
- `viewer/app.js` renders the front door through the legacy
  `/getting-started` route and points fallback copy at `docs/almanac/README.md`.
- `src/cli/commands/setup/next-steps.ts` counts markdown pages from all wiki
  roots.

## Health

- `src/wiki/health/index.ts` checks empty pages from indexed file paths and
  slug collisions across wiki roots using `page_id`.
