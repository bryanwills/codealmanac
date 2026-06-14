---
page_id: codealmanac-wiki
title: CodeAlmanac Wiki
topics: [concepts, architecture]
sources:
  - id: docs-layout-plan
    type: file
    path: docs/plans/2026-06-13-docs-almanac-layout.md
    note: Records the migration scope and the decision to make docs/almanac the canonical readable wiki.
  - id: decision-log
    type: file
    path: docs/plans/2026-06-13-docs-almanac-decision-log.md
    note: Records the content-root, legacy-compatibility, page_id, and topic ownership decisions.
---

# CodeAlmanac Wiki

This is the readable Almanac wiki for CodeAlmanac, the local codebase wiki
tool. It is written for a new maintainer: a human joining the repo or an agent
starting with no prior session context. [@docs-layout-plan]

The canonical wiki lives in `docs/almanac/`. `.almanac/` is runtime state for
generated files such as the SQLite index and job records. [@decision-log]

## Start Here

Read `_manual/README.md` before creating or moving pages. It defines the wiki's
page-selection, writing, and maintenance rules.

Use these sections as the primary browse map:

| Section | What belongs there |
| --- | --- |
| `concepts/` | Core vocabulary and mental models. |
| `architecture/` | Subsystems, runtime flows, storage, boundaries, and integration shape. |
| `guides/` | Task-oriented maintainer workflows. |
| `reference/` | Exact public contracts: commands, flags, config, formats, schemas, and APIs. |
| `decisions/` | Accepted choices and their rationale. |
| `incidents/` | Failures, migrations, regressions, and lessons that still matter. |
| `active/` | Current investigations before they settle into durable pages. |
| `context/` | Product, market, competitor, user, fundraising, and strategy background. |
| `_manual/` | How to write and maintain this wiki. |
| `_meta/` | Local conventions, coverage notes, migration notes, and wiki-maintenance state. |

## Runtime State

Readable wiki content belongs in `docs/almanac/`. Local runtime state belongs in
`.almanac/`, including `index.db`, job records, and run logs. SQLite is a
derived index, not the authoring source. [@decision-log]
