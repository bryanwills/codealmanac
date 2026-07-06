---
title: Lifecycle Runs
summary: Ingest and garden share one page-run workflow for harness execution and mutation safety.
topics: [architecture, operations, agents]
sources:
  - id: page-run
    type: file
    path: src/codealmanac/workflows/page_run/service.py
    note: Shared page-writing workflow for lifecycle operations.
  - id: ingest
    type: file
    path: src/codealmanac/workflows/ingest/service.py
    note: Ingest operation workflow.
  - id: garden
    type: file
    path: src/codealmanac/workflows/garden/service.py
    note: Garden operation workflow.
  - id: mutation
    type: file
    path: src/codealmanac/workflows/lifecycle_mutation.py
    note: Git snapshot and Almanac-root mutation policy.
  - id: runs
    type: file
    path: src/codealmanac/services/runs/store.py
    note: Run ledger repository and state transitions.
---

# Lifecycle Runs

`IngestWorkflow` resolves sources, loads runtime snapshots, renders the ingest prompt, and delegates the page-writing execution to `PageRunWorkflow` [@ingest] [@page-run]. `GardenWorkflow` prepares index and health context, renders the garden prompt, and delegates the same execution path [@garden] [@page-run].

`PageRunWorkflow` marks a run as running, records lifecycle events, executes the selected harness, records harness transcript and harness events, validates mutation safety, refreshes the index, and finishes the run [@page-run]. This keeps harness plumbing out of individual operation workflows.

Mutation policy snapshots Git status before the harness runs and validates that changed files stay under the configured `almanac/` root after the harness finishes [@mutation]. The current policy still requires a clean `almanac/` before lifecycle mutation; the product discussion says this should become more generous later.

The run store writes queued records, spec-backed queued records, events, harness transcript references, running transitions, terminal transitions, cancellation, and worker lock state [@runs].
