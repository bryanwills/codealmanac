# Retire Legacy Wiki Surfaces Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove retired wiki surfaces so the product has one clean durable docs model.

**Architecture:** `docs/almanac/` is the only durable wiki source tree. `.almanac/` is runtime state only. This pass keeps cross-wiki links and `almanac serve`, and does not rename build/absorb/sync/ingest vocabulary.

**Tech Stack:** TypeScript CLI, SQLite derived index, markdown/YAML docs.

---

## Scope

Remove:

- legacy `.almanac/pages` indexing and fallback
- legacy `.almanac/topics.yaml` topic fallback
- `.almanac/review.yaml`, the `almanac review` command, and viewer review UI
- mixed-mode layout logic
- archive/supersession query behavior
- `almanac migrate legacy-sources` as a permanent command
- `getting-started` as a viewer/front-door convention

Keep:

- cross-wiki links
- `almanac serve`
- `docs/almanac/README.md` as the front door
- `docs/almanac/topics.yaml` as source of truth
- `.almanac/index.db`, jobs, and runs as runtime state
- current operation naming in this pass

## Tasks

1. Simplify wiki layout helpers so page and topic roots point only to `docs/almanac`.
2. Remove review command/store/viewer API/UI references and tests.
3. Remove legacy source migration command wiring and tests.
4. Remove archive/supersession fields from frontmatter, schema, query filters, show/search flags, health, snapshots, and tests.
5. Remove `getting-started` fallback from viewer and prompt/docs references.
6. Update prompts/manual/docs to state the clean source/runtime split.
7. Run `npm run lint`, `npm test`, and `npm run build`.
8. Commit the deletion pass.
