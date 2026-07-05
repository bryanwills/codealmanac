---
title: Manual Overview
topics: []
---

# Manual Overview

This manual defines how agents maintain a CodeAlmanac repo-owned wiki.

Prompts name the job. The manual defines the writing rules, evidence bar, page
shape, and operation-specific workflow.

Read the relevant page before editing:

- `pages.md`: what deserves a page and how pages connect.
- `evidence.md`: how claims stay grounded and how conflicts are handled.
- `style.md`: how CodeAlmanac prose should read.
- `sources.md`: how raw material relates to wiki synthesis.
- `build.md`: how to create the first useful wiki.
- `ingest.md`: how to fold new material into an existing wiki.
- `garden.md`: how to improve an existing wiki graph.

Repo-specific conventions live in `almanac/README.md` and
`almanac/topics.yaml`.

## Folder Structure

The committed wiki source is a browseable Markdown tree under `almanac/`.

```text
almanac/
|-- README.md
|-- topics.yaml
|-- architecture/
|   |-- README.md
|   `-- indexing.md
|-- decisions/
|   `-- local-first.md
`-- guides/
    `-- setup.md
```

`almanac/README.md` plus `almanac/topics.yaml` identify an initialized
CodeAlmanac wiki.

Runtime state is local and rebuildable:

```text
~/.codealmanac/repos/<repo-id>/index.db
~/.codealmanac/repos/<repo-id>/runs/
```

Runtime files contain foreground run logs, queued background specs, worker
locks, and sync ledger state. They are not wiki source.
