---
title: Style
summary: Standing code-style principles for anyone writing or refactoring codealmanac.
topics: [style]
sources:
  - id: manual
    type: file
    path: MANUAL.md
    note: How-we-build rules these pages distill.
  - id: claude-md
    type: file
    path: CLAUDE.md
    note: Engineering taste section.
---

# Style

These pages hold the general principles that govern how codealmanac code is written and reorganized. They are deliberately not specific to any command or module: the reader is assumed to be an intelligent agent that can apply a principle to whatever code it is holding. Query them with `codealmanac search --topic style`.

The principles, in one breath: model all shaped data with Pydantic ([Types](types)); use clear, product-oriented, ideally one-word names ([Naming](naming)); organize code into layers with explicit boundaries and split wherever boundary pressure appears ([Boundaries](boundaries)); reach for a well-known library before hand-rolling anything ([Libraries](libraries)); and when refactoring, change architecture freely but never behavior ([Refactoring](refactoring)).

The established shape — services own product verbs, stores own persistence, request objects cross the service boundary, integrations implement service-owned ports, and `src/codealmanac/app.py` is the composition root — is the suggested requirement [@manual]. Depart from it only for an explicitly better architecture, argued in writing, never by drift.

When judgment is needed beyond these pages, the reference library is `docs/reference/cosmic-python/` — all chapters, not only the ones mapped in CLAUDE.md — plus the taste rules in MANUAL.md [@manual] [@claude-md].
