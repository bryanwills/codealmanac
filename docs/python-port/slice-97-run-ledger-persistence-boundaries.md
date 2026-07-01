# Slice 97 - Run Ledger Persistence Boundaries

Date: 2026-07-01

## Scope

Split the run ledger store into explicit persistence responsibilities without
changing the public `jobs` or lifecycle behavior:

- path construction and run-id validation
- JSON record/spec and JSONL event IO
- worker lock ownership
- state-transition writes that keep record updates and status events together

This slice is architecture and correctness work for the existing foreground and
background job machinery. It does not add new CLI verbs, scheduler policy, or
provider behavior.

## Why Now

`services/runs/store.py` had become the one file for every run-ledger concern:
path validation, atomic JSON writes, JSONL events, queue specs, worker locks,
status transitions, and service-facing repository methods. The current store
also wrote a status record and then appended the matching status event through
separate low-level calls in `mark_running`, `finish`, and `cancel`.

The live agreement makes durable run events first-class. Jobs attach/cancel,
viewer job detail, sync reconciliation, and background worker execution all
depend on the run record and log telling the same story.

## Decisions

- Keep `RunStore` as the repository facade used by `RunsService`.
- Put run path validation in `services/runs/paths.py`.
- Put record/spec/event file mechanics in `services/runs/io.py`.
- Put worker lock mechanics in `services/runs/locks.py`.
- Put grouped record-plus-event state transitions in
  `services/runs/transitions.py`.
- Do not introduce a generic Unit of Work abstraction across the whole app.
  The filesystem ledger is not a database transaction boundary, so the useful
  seam is a small run-specific transition writer.

## Shape

```python
record = store.read(almanac_path, run_id)
running = record.model_copy(update={"status": RunStatus.RUNNING, ...})

store.transitions.write_status_transition(
    almanac_path,
    previous=record,
    record=running,
    timestamp=now,
    message="running",
)
```

`RunTransitionWriter` writes through `RunLedgerIO` and owns the best-effort
rollback when event append fails after a record rewrite. Callers no longer
manually pair `write_record(...)` and `append_event(...)`.

## Cosmic Python Transfer

Chapter 6 calls UoW "our abstraction over the idea of _atomic operations_" and
says it gives "a way to persist all of our changes at once" in
`docs/reference/cosmic-python/chapter_06_uow.md`. This slice applies that idea
locally: state transitions are grouped at the run-ledger boundary instead of
being hand-paired in service-facing methods.

The same chapter warns that rollback and nested transactions need careful
thought. We are not pretending the filesystem has SQL transaction semantics;
the writer is a bounded seam for this store's two-file transition contract.

## Files

- `src/codealmanac/services/runs/store.py`
- `src/codealmanac/services/runs/paths.py`
- `src/codealmanac/services/runs/io.py`
- `src/codealmanac/services/runs/locks.py`
- `src/codealmanac/services/runs/transitions.py`
- `tests/test_runs_service.py`
- `tests/test_architecture.py`
- `docs/python-port/idea-evolution.md`
- `docs/python-port/ownership-map.md`
- `docs/python-port/next-agent-brief.md`

## Verification

Focused:

```bash
uv run pytest tests/test_runs_service.py tests/test_run_queue_workflow.py tests/test_architecture.py
uv run ruff check src/codealmanac/services/runs tests/test_runs_service.py tests/test_run_queue_workflow.py tests/test_architecture.py
```

Broad:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
