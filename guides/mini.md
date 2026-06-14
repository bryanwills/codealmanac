# Almanac — A Wiki For This Codebase

This repo may have a durable wiki under `docs/almanac/`. It is written for
humans and coding agents: concepts, decisions, flows, incidents, constraints,
and change paths that the code alone does not explain.

`.almanac/` is runtime state only: index database, jobs, logs, config, and sync
ledger. Do not look there for wiki prose.

## Mental Model

- **Pages** are Markdown files under `docs/almanac/`. `README.md` is the front
  door. Nested folders are the browse structure.
- **Page identity** comes from `page_id` when present; otherwise the filename is
  kebab-cased. Use stable `page_id` values when pages may move.
- **Topics** live in `docs/almanac/topics.yaml` and page frontmatter. They form a
  DAG, not a folder replacement.
- **Sources** live in frontmatter. `sources: [{ type: "file", path: "src/x.ts" }]`
  is the authored way to connect a page to code. File sources and inline
  `[[src/x.ts]]` links create derived file references for `--mentions`.
- **Links** use one syntax:
  - `[[checkout-flow]]` -> page
  - `[[src/checkout/handler.ts]]` -> file
  - `[[src/checkout/]]` -> folder
  - `[[openalmanac:supabase]]` -> cross-wiki page

Read `docs/almanac/README.md` first when the task touches a real subsystem.

## When To Use It

Use the wiki before changing subsystems, external integrations, runtime flows,
data models, job machinery, prompts, or anything with history.

Skip it for pure typo fixes, tiny local edits, or when the user explicitly asks
you to inspect one file.

Code is still the authority. If code and wiki disagree, trust code and mention
the stale page in your response.

## Core Commands

```bash
almanac search "checkout timeout"
almanac search --mentions src/checkout/handler.ts
almanac search --mentions src/checkout/
almanac search --topic auth
```

`search` prints slugs. Empty stdout with `# 0 results` on stderr means the query
worked and matched nothing.

```bash
almanac show checkout-flow
almanac show checkout-flow --lead
almanac show checkout-flow --meta
almanac show checkout-flow --files
almanac show checkout-flow --backlinks
```

`--files` prints derived file references from structured file sources and inline
file links.

```bash
almanac topics
almanac topics show auth --descendants
almanac health
almanac serve
```

Use `health` after moving/deleting code or cleaning the wiki. It reports graph
and source problems; it does not rewrite pages.

## Writing Pages

You usually do not write pages during ordinary coding work. Scheduled sync and
lifecycle jobs update the wiki from durable session knowledge. Write directly
only when the user asks for wiki maintenance or an obvious correction is needed.

Use this frontmatter shape:

```yaml
---
page_id: checkout-flow
title: Checkout Flow
description: How checkout moves from request to paid order.
topics: [flows, payments]
sources:
  - id: checkout-handler
    type: file
    path: src/checkout/handler.ts
    note: Handles checkout submission.
---
```

Then cite non-obvious claims with `[@checkout-handler]`.

Writing standard:

- Every paragraph should contain concrete project facts.
- Prefer prose over bullets unless the page is genuinely listing things.
- Preserve old knowledge in prose when it explains the current design.
- Do not speculate. Say what is known, or omit the claim.
- Use `[[...]]` links when they help the reader move through related pages,
  files, or folders.

## Troubleshooting

```bash
almanac doctor
almanac sync status
almanac jobs
almanac jobs show <job-id>
almanac jobs logs <job-id>
```

Runtime files live under `.almanac/jobs/` and `.almanac/index.db`. Durable wiki
source lives under `docs/almanac/`.

When in doubt:

- `docs/almanac/README.md` — repo-specific reading map
- `docs/almanac/_manual/` — wiki maintenance manual when present
- `almanac --help` / `almanac <command> --help` — installed command surface
