# Docs Almanac Layout Refactor Audit

Date: 2026-06-13

## Goal

Critically audit the `docs/almanac/` migration branch to determine which
architecture, boundaries, names, compatibility paths, and workflows should be
preserved, simplified, removed, or redesigned before this layout becomes the
long-term wiki foundation.

## Scope

This audit covers the branch `codex/docs-almanac-layout` relative to
`origin/dev`. It focuses on wiki content roots, runtime state, topic files,
indexing, health checks, viewer behavior, setup messaging, prompts, and the new
manual/docs structure.

## Verdict

The direction is correct: readable wiki content belongs under `docs/almanac/`,
runtime state belongs under `.almanac/`, and `page_id` is the right stable
identity for nested docs pages.

The remaining risk is architectural drift during migration. The branch has a
new central `src/wiki/locations.ts`, but several behaviors still encode layout
policy locally. The next refactor should turn "where wiki things live" into one
explicit workspace/layout boundary instead of a set of helpers that callers
combine manually.

## Audit Files

- `worklog.md` records the audit sequence and verification.
- `source-map.md` maps the touched code and docs surfaces.
- `smells.md` records architectural concerns.
- `feature-questions.md` challenges product and workflow surface area.
- `hand-rolled-inventory.md` reviews custom machinery.
- `research-notes.md` records prior-art observations used by the audit.
- `target-architecture.md` proposes the cleaner shape.
- `refactor-roadmap.md` lists follow-up work.
- `reports/` contains subagent findings when available.
