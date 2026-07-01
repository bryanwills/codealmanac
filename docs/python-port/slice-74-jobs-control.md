# Slice 74 - Jobs Control Surface

Date: 2026-07-01

## Scope

Restore the durable jobs control contract that the background worker will use:

- `codealmanac jobs attach <run-id>`
- `codealmanac jobs cancel <run-id>`
- service/store support for cancelling queued or running runs
- terminal finalization that does not resurrect cancelled runs

This slice does **not** implement the queue worker yet. It builds the shared
control seam first so foreground execution, future background execution, CLI,
tests, and viewer APIs can all use the same run ledger behavior.

## Why Now

The live agreement says background jobs are in scope again: per-wiki queue,
worker lock, durable spec files, append-only event logs, attach, cancel, stale
lock handling, and foreground execution through the same services.

The current Python code has `jobs`, `jobs show`, and `jobs logs`, but no control
verbs. Adding a worker before cancellation/finalization semantics exist would
force the worker to invent its own lifecycle behavior.

## Decisions

- Keep public noun `jobs`; keep internal service noun `runs`.
- Add cancellation through `RunsService`, not through CLI file edits.
- Cancel only `queued` or `running` runs. Terminal runs are a no-op result.
- Final `finish(...)` must preserve an already-cancelled record instead of
  overwriting it as `done` or `failed`.
- `attach` replays the durable log and, when not terminal, can poll until the
  record becomes terminal. The CLI default can be simple; the service shape must
  support the later worker.
- Do not add background process spawning in this slice.
- Do not add a parallel `JobService`. `RunsService` remains the durable ledger
  owner; the worker later becomes an executor over `RunsService` and operation
  specs.

## Shape

```python
cancelled = app.runs.cancel(
    CancelRunRequest(cwd=Path.cwd(), wiki=args.wiki, run_id=args.run_id)
)

attached = app.runs.attach(
    AttachRunRequest(cwd=Path.cwd(), wiki=args.wiki, run_id=args.run_id)
)
```

The store owns atomic record rewrites and event appends:

```python
if record.status in TERMINAL_RUN_STATUSES:
    return RunCancelResult(record=record, changed=False)

cancelled = record.model_copy(update={status: CANCELLED, finished_at: now})
write_record(...)
append_event(..., kind=STATUS, message="cancelled")
```

`finish(...)` re-reads the record and returns a cancelled record unchanged when
another actor already cancelled it.

## Cosmic Python Transfer

Chapter 4 describes an application service as the layer that handles requests
from the outside world and orchestrates simple steps. `cancel` and `attach` are
use cases over the run ledger; the CLI should call service methods, not edit
JSON files.

Chapter 13 keeps dependency wiring in the composition root. This slice keeps
that direction by extending `RunsService`; it does not make CLI dispatch create
stores, probes, or workers.

## Files

- `src/codealmanac/services/runs/models.py`
- `src/codealmanac/services/runs/requests.py`
- `src/codealmanac/services/runs/service.py`
- `src/codealmanac/services/runs/store.py`
- `src/codealmanac/cli/parser/admin.py`
- `src/codealmanac/cli/dispatch/admin.py`
- `src/codealmanac/cli/render/admin.py`
- `tests/test_runs_service.py`
- `tests/test_cli.py`
- `tests/test_architecture.py`
- steering docs under `docs/python-port/`

## Verification

Run focused checks:

```bash
uv run pytest tests/test_runs_service.py tests/test_cli.py tests/test_architecture.py
uv run ruff check src/codealmanac/services/runs src/codealmanac/cli tests/test_runs_service.py tests/test_cli.py tests/test_architecture.py
```

Then run broad checks:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
