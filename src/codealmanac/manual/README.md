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
- `init.md`: how to create the first useful wiki.
- `ingest.md`: how to fold new material into an existing wiki.
- `garden.md`: how to improve an existing wiki graph.

Repo-specific conventions live in `README.md` and `topics.yaml` under the
configured Almanac root.

## Folder Structure

The configured Almanac root is flat. A new repo defaults to `almanac/`, but a
repo may explicitly use another safe repo-relative directory such as
`docs/almanac/` or `.almanac/`.

```text
<almanac-root>/
|-- README.md
|-- topics.yaml
|-- pages/
|-- manual/
```

`topics.yaml` plus `pages/` identify an initialized CodeAlmanac wiki. `README.md`
is guidance for readers and writers, not a marker by itself.

Runtime state is local and rebuildable:

```text
<almanac-root>/index.db
<almanac-root>/index.db-wal
<almanac-root>/index.db-shm
<almanac-root>/jobs/
```

`jobs/` contains foreground run logs, queued background specs, worker locks,
and sync ledger state. It is not wiki source.
