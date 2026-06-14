---
page_id: wiki-conventions
title: Wiki Conventions
topics: [concepts]
sources:
  - id: decision-log
    type: file
    path: docs/plans/2026-06-13-docs-almanac-decision-log.md
    note: Records local conventions for docs/almanac.
---

# Wiki Conventions

This page records local conventions for the CodeAlmanac wiki. Update it when
folder, naming, source, citation, migration, or coverage rules change.

## Current Conventions

- `docs/almanac/README.md` is the front door.
- `docs/almanac/topics.yaml` is the canonical topic file.
- `.almanac/` stores runtime state only.
- New pages use `page_id`, `title`, `topics`, and `sources`.
- `description` is optional; the lead should usually preview the page.
- `_manual/` explains how to maintain the wiki.
- `_meta/` records conventions, coverage, and source gaps.

## Old Knowledge

When older context still explains the current repo, preserve it in the page that
owns the subject. Do not maintain a second legacy page tree.
