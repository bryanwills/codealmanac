# Docs Almanac Layout

Date: 2026-06-13

## Goal

Move the canonical human-readable wiki shape toward `docs/almanac/` while
keeping `.almanac/` as repo-local runtime state. The first slice should make the
new location usable by tooling and seed the manual/navigation structure. It
should not perform a full semantic rewrite of the existing `.almanac/pages`
corpus.

## Decisions

- Canonical readable wiki content lives under `docs/almanac/`.
- `.almanac/` remains the runtime home for `index.db`, jobs, runs, and other
  local state.
- `docs/almanac/topics.yaml` is the canonical topic DAG for the new layout.
  The database indexes it but does not own it.
- Existing `.almanac/pages` content remains readable during migration.
- Nested docs require stable `page_id` frontmatter so `README.md` files and
  repeated filenames do not collide.
- The wiki is human-first and agent-queryable. Pages should read like articles,
  with source refs, wikilinks, and clear navigation.

## Scope

- Add shared path helpers for wiki content roots, pages roots, topics file, and
  runtime paths.
- Update indexing/freshness/snapshots/topic rewrites to use the helpers.
- Add `page_id` parsing and slug selection.
- Update prompts to refer to `docs/almanac/`, `_manual`, `_meta`, and the new
  article standard.
- Seed `docs/almanac/` with navigation, manual pages, and a small set of hub
  pages.
- Add focused tests for the new content path and `page_id`.

## Out Of Scope

- Full rewrite of existing wiki pages into the new structure.
- Removing legacy `.almanac/pages` support.
- Hosted/GitHub product changes.
- A new status taxonomy for `active/`.
- Moving review queues or job runtime records out of `.almanac/`.

## Verification

- `npm test -- indexer init-helper build-operation garden-operation absorb-operation`
- Broader `npm test` if the focused suite is green.
