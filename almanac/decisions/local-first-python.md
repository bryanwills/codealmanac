---
title: Local-First Python
summary: e773dc0b is the fork point for the right local Python product.
topics: [decisions, architecture, migration]
sources:
  - id: agreement
    type: file
    path: docs/python-port-live-agreement.md
    note: Active rewrite agreement.
  - id: notes
    type: file
    path: notes.md
    note: Product discussion notes and history decision.
  - id: tickets
    type: file
    path: implementation-tickets.md
    note: Ordered rebuild tickets.
  - id: readme
    type: file
    path: README.md
    note: Public README contract.
---

# Local-First Python

`e773dc0b` is the fork point for the right local Python product [@agreement] [@notes]. Later `dev` and `main` moved ahead on hosted and cloud product work that this branch treats as reference material only [@agreement].

The public product is named `codealmanac`, uses `almanac/` as the only repo wiki root, and uses `~/.codealmanac/` for user state [@readme] [@agreement]. It does not preserve public `almanac` or `alm` aliases, alternate roots, hosted login, connect, upload, a public SDK surface, MCP, or migration compatibility [@agreement].

The rebuild tickets are ordered so the product contract lands before storage shape, source evidence, Markdown links, runtime-state relocation, validation, and prompt/manual import [@tickets]. Ticket 2.5 migrates useful memory from the old repo wiki without keeping the old product model [@tickets].
