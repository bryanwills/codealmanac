# Slice 37 - Sync Pending Run Linkage

Date: 2026-06-29

## Scope

Foreground `sync` now links each pending ledger claim to the Ingest run that
will process the claimed transcript range. The slice does not add a background
queue, hosted sync, or unattended retry scheduler.

## Shape

```python
ingest_request = RunIngestRequest(...)
run = ingest.start(ingest_request)
ledger.claim(run.run_id, transcript_range)
result = ingest.run_with_run(RunIngestWithRunRequest(..., run_id=run.run_id))
```

`IngestWorkflow.run(...)` remains the public workflow call. It now delegates to
`start(...)` plus `run_with_run(...)`, so sync can create the run record before
it writes the pending claim.

The sync ledger pending claim records:

- `pending_run_id`
- `pending_to_size`
- `pending_prefix_hash`
- `pending_from_line`
- `pending_to_line`

## Reconciliation

`sync status` is read-only:

- linked `queued` or `running` runs are skipped as `sync-pending-run-active`
- linked terminal `done` runs report `sync-pending-run-done`
- linked terminal `failed` or `cancelled` runs report `sync-pending-run-failed`

Foreground `sync` reconciles before cursor evaluation:

- linked `done` runs promote the pending cursor into the durable absorbed cursor
- linked `failed` or `cancelled` runs clear pending fields and retry from the
  last successful cursor if the transcript prefix still matches
- active linked runs stay pending
- missing run ids fall back to the existing stale-pending timeout path

## Cosmic Python Note

Chapter 8's event/message-bus lesson is the useful pattern here: separate the
fact that happened from the side effect that reacts to it. In CodeAlmanac, the
run lifecycle transition is the durable fact and sync reconciliation is the
reaction.

A finite-state-machine library is not used in this slice. `transitions` and
`python-statemachine` are real options, but the current behavior is a small
persisted enum transition plus ledger reconciliation. A statechart library
would add machinery before there is a second lifecycle state machine to share.

## Verification Plan

- focused sync workflow tests
- focused ingest workflow tests
- focused ruff over ingest/sync and tests
- full pytest
- full ruff
- `git diff --check`
- dogfood with an isolated temp repo, linked terminal pending run, foreground
  sync, final ledger readback, and prompt cursor check
