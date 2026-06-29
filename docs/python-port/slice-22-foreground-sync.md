# Slice 22 - Foreground Sync Execution

Date: 2026-06-29

## Scope

Add write-capable local `codealmanac sync`.

This slice runs foreground Ingest for each ready transcript. It does not add a
background runner, scheduler automation, or pending-run reconciliation.

## Architecture

`SyncWorkflow` now has two public verbs:

- `status(...)` returns the read-only readiness view.
- `run(...)` reuses the same eligibility evaluation, then calls
  `IngestWorkflow.run(...)` for each ready transcript.

The CLI remains a thin adapter:

```text
codealmanac sync status   -> app.workflows.sync.status(...)
codealmanac sync          -> app.workflows.sync.run(...)
```

Sync passes transcript material to Ingest as:

```text
transcript:<absolute transcript path>
```

The Ingest guidance includes the sync cursor: app, session id, transcript path,
previously absorbed line/byte, and the line where the agent should focus.

## Ledger Rule

The Python port currently has foreground lifecycle execution. For this shape,
the safe Unit-of-Work boundary is:

1. discover and evaluate transcript work
2. run Ingest
3. advance `.almanac/jobs/sync-ledger.json` only after Ingest succeeds

This is intentionally different from the archived background TypeScript sync,
which wrote pending cursor ownership before enqueueing a background Absorb job.
Pending state belongs with a real background owner and reconciliation loop.

## Failure Behavior

If one transcript's Ingest fails, sync marks that transcript entry `failed`,
adds it to `needs_attention`, and continues with the remaining ready
transcripts. The failed Ingest run still owns its own run record.

## Verification

- focused sync workflow and CLI tests
- full pytest suite
- ruff
- `git diff --check`
- isolated foreground sync dogfood with a fake Codex transcript and fake Codex
  harness
