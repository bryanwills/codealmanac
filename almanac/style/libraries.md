---
title: Libraries
summary: Research a well-known library before hand-rolling anything.
topics: [style]
sources:
  - id: pyproject
    type: file
    path: pyproject.toml
    note: Current dependency set.
  - id: claude-md
    type: file
    path: CLAUDE.md
    note: Open-source surface-area rule.
---

# Libraries

Do not hand-roll what a well-known library already does. Before writing parsing, formatting, retry, scheduling, or terminal machinery, research the obvious library first — mature libraries routinely have exact support for the output or behavior wanted, in corners of their API that are easy not to know about.

The preference order is: the standard library, then a dependency already in `pyproject.toml` [@pyproject], then a new well-known library, and hand-rolling only last. The dependencies already installed have unused depth — check them before adding anything.

The counterweight: this is an open-source project, and every dependency is public surface and maintenance burden [@claude-md]. Adding a new dependency needs a one-line justification (what was researched, why existing deps did not cover it). A large dependency for a small need is worse than a small honest hand-roll.
