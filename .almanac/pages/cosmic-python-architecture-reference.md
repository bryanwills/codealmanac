---
title: Cosmic Python Architecture Reference
summary: The Python rewrite uses Architecture Patterns with Python as a local reference for service layers, repositories, units of work, and composition roots, but does not copy the book's exact application shape.
topics: [stack, decisions, systems]
sources:
  - id: cosmic-readme
    type: file
    path: docs/reference/cosmic-python/README.md
    note: Lists the vendored Architecture Patterns with Python chapters.
  - id: cosmic-license
    type: file
    path: docs/reference/cosmic-python/LICENSE.md
    note: Records the CC-By-ND license for the local reference copy.
  - id: cosmic-repository
    type: file
    path: docs/reference/cosmic-python/chapter_02_repository.md
    note: Defines the repository pattern and dependency inversion around persistence.
  - id: cosmic-service-layer
    type: file
    path: docs/reference/cosmic-python/chapter_04_service_layer.md
    note: Defines the service layer as the use-case boundary.
  - id: cosmic-uow
    type: file
    path: docs/reference/cosmic-python/chapter_06_uow.md
    note: Defines Unit of Work as an abstraction for atomic operations.
  - id: cosmic-di
    type: file
    path: docs/reference/cosmic-python/chapter_13_dependency_injection.md
    note: Explains dependency injection and the composition root.
  - id: local-notes
    type: file
    path: docs/reference/cosmic-python/CODEALMANAC.md
    note: Maps Cosmic Python chapters to CodeAlmanac's service/workflow/integration structure.
  - id: live-agreement
    type: file
    path: docs/python-port-live-agreement.md
    note: Records the active Python rewrite structure and local-only v1 scope.
status: active
verified: 2026-06-29
---

# Cosmic Python Architecture Reference

The Python rewrite vendors Architecture Patterns with Python under `docs/reference/cosmic-python/` as a Markdown-only architecture reference. The local copy is from `cosmicpython/book` commit `d4522c44ed89eb320ad9eed2525d2af3b149bd3f`, and its source repo declares a `Creative Commons CC-By-ND` license. Keep the generated Markdown files as book text; put CodeAlmanac-specific interpretation in local notes or wiki pages. [@cosmic-readme] [@cosmic-license] [@local-notes]

## What Carries Over

The book's useful transfer is the dependency direction, not its exact package names. CodeAlmanac keeps product contracts in `services/*`, multi-service verbs in `workflows/*`, concrete adapters in `integrations/*`, and dependency wiring in `src/codealmanac/app.py`. [@live-agreement] [@local-notes]

`chapter_02_repository.md` supports the rule that persistence code belongs behind store abstractions. In CodeAlmanac, that maps to `store.py`, `*_store.py`, `records.py`, and service tests with thin fakes. [@cosmic-repository] [@local-notes]

`chapter_04_service_layer.md` supports the rule that CLI commands call service/workflow verbs instead of owning product behavior. The chapter says the service layer defines "the use cases of our system"; CodeAlmanac's equivalent is service-owned verbs plus workflow-owned coordination. [@cosmic-service-layer] [@live-agreement]

`chapter_06_uow.md` supports explicit transaction ownership. The chapter frames Unit of Work around "atomic operations"; CodeAlmanac should express that through service/workflow transaction boundaries rather than hidden SQLite side effects. [@cosmic-uow] [@live-agreement]

`chapter_13_dependency_injection.md` supports a composition root. CodeAlmanac's composition root is `src/codealmanac/app.py`, where integrations are wired into service-owned ports. [@cosmic-di] [@live-agreement]

## What Does Not Carry Over

Do not copy the book's allocation-domain package structure literally. CodeAlmanac's product nouns are workspaces, wiki, index, sources, runs, harnesses, automation, config, and diagnostics. The old TypeScript code under `archive/code/` remains behavior reference, while the live Python structure is recorded in `docs/python-port-live-agreement.md`. [@live-agreement] [@local-notes]

Do not transform the full book into `.almanac` pages. The license allows a reference copy, but wiki pages should contain CodeAlmanac-specific notes and short quotations only. [@cosmic-license] [@local-notes]
