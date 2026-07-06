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
  - id: run-spec
    type: file
    path: src/codealmanac/services/runs/models.py
    note: Durable queued run spec shape.
  - id: queue
    type: file
    path: src/codealmanac/workflows/run_queue/service.py
    note: Queued lifecycle run persistence and rehydration.
  - id: commit-policy
    type: file
    path: src/codealmanac/workflows/lifecycle_commit.py
    note: Prompt-facing lifecycle commit policy.
  - id: runtime
    type: file
    path: src/codealmanac/services/workspaces/runtime.py
    note: Per-workspace runtime path mapping.
  - id: validation
    type: file
    path: src/codealmanac/services/health/service.py
    note: Validation service used before lifecycle success.
---

# Lifecycle Runs

`IngestWorkflow` resolves sources, loads runtime snapshots, renders the ingest prompt, and delegates the page-writing execution to `PageRunWorkflow` [@ingest] [@page-run]. `GardenWorkflow` prepares index and health context, renders the garden prompt, and delegates the same execution path [@garden] [@page-run].

Lifecycle prompts include a `source_control` context block that carries whether auto-commit is allowed, the wiki source files agents may commit, forbidden file categories, and the `almanac: <summary>` commit-message shape [@ingest] [@garden] [@commit-policy]. Background runs persist that policy in the durable run spec and restore it before running the harness [@queue] [@run-spec].

`PageRunWorkflow` marks a run as running, records lifecycle events, executes the selected harness, records harness transcript and harness events, validates mutation safety, refreshes the index, runs wiki validation, and finishes the run [@page-run] [@validation]. This keeps harness plumbing out of individual operation workflows.

Mutation policy snapshots Git status before the harness runs and validates that files changed during the run stay under the configured `almanac/` root after the harness finishes [@mutation]. A run may start with pre-existing user edits in `almanac/`; the before/after comparison is what decides what the agent changed [@mutation].

The run store writes queued records, spec-backed queued records, events, harness transcript references, running transitions, terminal transitions, cancellation, and worker lock state under the per-workspace runtime directory [@runs] [@runtime].
