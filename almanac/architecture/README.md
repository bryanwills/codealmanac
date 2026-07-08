---
title: Architecture
topics: [architecture, overview]
sources:
  - id: manual
    type: file
    path: MANUAL.md
    note: Repo rule that features should reshape architecture before implementation when the current shape does not hold.
  - id: topics
    type: file
    path: almanac/topics.yaml
    note: Topic graph showing the major architecture neighborhoods.
  - id: service-boundaries
    type: file
    path: almanac/architecture/service-boundaries.md
    note: Architecture page for layer ownership and dependency direction.
  - id: composition-root
    type: file
    path: almanac/architecture/composition-root.md
    note: Architecture page for application graph assembly.
  - id: lifecycle-workflows
    type: file
    path: almanac/architecture/lifecycle/workflows.md
    note: Architecture page for build, ingest, garden, sync, and operation execution.
  - id: index-search
    type: file
    path: almanac/architecture/wiki/index-refresh-and-search.md
    note: Architecture page for index refresh and read-side search.
---

# Architecture

Architecture pages explain the system areas that future work must preserve or reshape before adding behavior. The repo manual makes this explicit: implementation work should evolve the codebase so the feature fits, and should stop when the current shape cannot hold the request cleanly [@manual]. This hub gives the shortest route through the architecture cluster instead of requiring readers to scan every page under `architecture/`.

The architecture topic has focused child neighborhoods for wiki behavior, lifecycle operations, agent runs, CLI behavior, repositories, local state, automation, setup, runtime resources, persistence, sources, and the viewer [@topics]. Read the page that owns the boundary you plan to change, then follow its links into guides, decisions, or reference pages.

## Core Shape

Start with [Service boundaries](service-boundaries). It explains the main dependency direction: CLI adapters enter through the app, workflows coordinate product operations, services own product verbs, stores own persistence, ports describe outside capabilities, and integrations implement those ports [@service-boundaries].

[Composition root](composition-root) is the companion page for construction. It explains how `src/codealmanac/app.py` assembles stores, services, adapters, operation runners, and workflows into one application graph [@composition-root].

## Page-Writing Operations

[Lifecycle workflows](lifecycle/workflows) is the entry point for build, ingest, garden, and sync. Build, ingest, and garden are page-writing operation families; sync is a scanner that queues ingest work instead of writing pages itself [@lifecycle-workflows].

Use [Operation runner](lifecycle/operation-runner) when changing the shared run-execution path. Use [Mutation safety](lifecycle/mutation-safety) when changing the checks that keep lifecycle writes inside the allowed wiki source files.

## Read Side And Wiki Graph

[Index refresh and search](wiki/index-refresh-and-search) explains the derived SQLite read model, implicit refresh before read commands, FTS search, topic filters, and mention search [@index-search].

For authored wiki contracts, read [Page identity](wiki/page-identity), [Path normalization and file refs](wiki/path-normalization-and-file-refs), [Topics DAG](wiki/topics-dag), and [Health and validation](wiki/health-and-validation). These pages define how Markdown routes, sources, topics, and validation fit together.

## Edges And Interfaces

Use [CLI adapter boundary](cli/adapter-boundary) and [Terminal output](cli/terminal-output) for command entrypoints and rendering. Use [Harness contract](agent-runs/harness-contract) and [Provider adapters](agent-runs/provider-adapters) for Codex and Claude execution boundaries. Use [Source resolution and runtime](sources/source-resolution-and-runtime) when changing ingest inputs or source adapters.

[Local state](repositories/local-state), [Selection and root](repositories/selection-and-root), and [SQLite store boundaries](persistence/sqlite-store-boundaries) explain repository selection, runtime paths, and persistence ownership. [Local viewer](viewer/local-viewer) explains the browser UI that projects the same wiki, topics, files, and jobs.
