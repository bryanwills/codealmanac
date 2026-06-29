# Slice 36 - Run Lifecycle State

Date: 2026-06-29

## Scope

Run records should represent the lifecycle state of write-capable work. A run
starts as `queued`, moves to `running` when a workflow begins side-effecting
work, and finishes with a terminal status.

## Non-goals

- No background queue.
- No sync pending run id yet.
- No scheduler change.
- No public CLI command change.

## Design

`RunsService.mark_running(...)` delegates to `RunStore.mark_running(...)`.
The store updates `status`, `started_at`, and `updated_at`, then appends a
`running` status event. Calling it for an already running run is idempotent.
Calling it for a terminal run raises a conflict.

Ingest and Garden call `mark_running(...)` after creating their run record and
before preflight/source/harness work. This keeps lifecycle status transitions in
the `runs` service and gives future sync reconciliation a trustworthy run-state
source.

This follows Cosmic Python chapter 7's aggregate/consistency-boundary pressure:
the run record is the aggregate that owns its lifecycle invariants.

## Verification

- `uv run pytest tests/test_runs_service.py tests/test_ingest_workflow.py tests/test_garden_workflow.py tests/test_sync_workflow.py` - 30 passed
- `uv run ruff check src/codealmanac/services/runs src/codealmanac/workflows/ingest src/codealmanac/workflows/garden tests/test_runs_service.py tests/test_ingest_workflow.py tests/test_garden_workflow.py` - passed
- Live dogfood passed: a temp-repo Ingest run through a fake harness produced
  `jobs show --json` status `done` with `started_at`/`finished_at`, and
  `jobs logs --json` status messages `queued ingest`, `running`, `done`.
- `uv run pytest` - 175 passed
- `uv run ruff check .` - passed
- `git diff --check` - passed
