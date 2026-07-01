# Slice 109 - Sync Execution Boundaries

## Scope

Move sync run execution effects out of `SyncWorkflow.service` while preserving
foreground and background sync behavior.

## Why Now

After slice 108, `workflows/sync/service.py` is the largest production file.
Its `evaluate(...)` method is already policy-oriented and delegates most cursor
logic to sync policy modules. Its `run(...)` method still mixes high-level sync
orchestration with foreground Ingest execution, background queueing, pending
claim writes, worker spawn failure handling, failed ledger writes, absorbed
ledger writes, and started summary rows.

Cosmic Python chapter 04 separates orchestration logic from interfacing code,
and chapter 13 keeps dependencies explicit. Applied here: `SyncWorkflow` should
own the public `status/run/evaluate` use case surface, while a focused executor
owns the side effects that turn evaluated work items into run records and ledger
updates.

## In Scope

- Add `workflows/sync/execution.py` with `SyncRunExecutor`.
- Keep `SyncWorkflow.run(...)` as the public workflow verb.
- Move foreground ingest execution, background queueing, worker spawn failure
  handling, pending/failed/absorbed ledger writes, and started rows into the
  executor.
- Add an architecture guard so `service.py` does not regrow execution
  mechanics.

## Out of Scope

- Sync policy changes.
- Public CLI command changes.
- Background default-mode changes.
- Ledger schema changes.

## Verification

- Focused sync workflow tests for foreground/background/failure paths.
- Architecture guard for sync service/execution split.
- Public `sync status --json` dogfood.
- Full pytest, Ruff, and diff hygiene.
