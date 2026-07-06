from pathlib import Path


def starter_readme() -> str:
    return """---
title: CodeAlmanac Wiki
topics: [concepts]
sources: []
---

# CodeAlmanac Wiki

This is the living wiki for this repository. It records the durable knowledge
the code cannot say: decisions, flows, invariants, incidents, gotchas, and
project context that future agents should not rediscover from scratch.

## Notability Bar

Write a page when it preserves non-obvious knowledge that will help a future
agent work safely in this codebase.

Good pages explain:

- a decision that took research or trial-and-error
- a cross-file flow
- an invariant or gotcha not visible from one file
- an external dependency as this repo uses it
- a product or operational constraint that shapes future work

Do not write pages that restate nearby code.

## Topic Taxonomy

Topics live in `topics.yaml`. Pages are Markdown files directly under
`almanac/`, including nested folders.

## Links

Use normal Markdown links between pages. Put file evidence in `sources:`.
"""


def starter_topics_yaml() -> str:
    return """topics:
  - slug: concepts
    title: Concepts
    description: Core vocabulary and mental models for this codebase
    parents: []
"""


def starter_page() -> str:
    return """---
title: Getting Started
topics: [concepts]
sources: []
status: active
---

# Getting Started

This starter page marks the wiki as initialized. Replace it with the first
durable reading path for this repository.
"""


def gitignore_runtime_block(almanac_root: Path) -> list[str]:
    root = almanac_root.as_posix().rstrip("/")
    return [
        f"{root}/index.db",
        f"{root}/index.db-wal",
        f"{root}/index.db-shm",
        f"{root}/jobs/",
    ]
