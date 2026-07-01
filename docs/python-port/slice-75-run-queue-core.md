# Slice 75 - Run Queue Core

Date: 2026-07-01

## Scope

Restore the core queue machinery behind background jobs:

- durable run specs beside run records
- oldest queued run selection
- per-wiki worker lock
- stale lock recovery
- in-process worker drain that executes queued Ingest and Garden specs

This slice does **not** spawn a detached background process yet, and it does not
add public `--background` / `--foreground` lifecycle flags. It builds the
execution core that those surfaces will call.

## Why Now

Slice 74 restored `jobs attach` and `jobs cancel`, but cancellation only becomes
useful for background work when queued work has a durable spec and a worker can
claim it through one serialized path.

The archived implementation used this split:

- `spec.ts` persisted executable operation specs
- `queue.ts` owned the per-wiki worker lock and oldest queued lookup
- `worker.ts` drained queued jobs
- `executor.ts` ran one job and finalized the record

The Python shape should reuse that product split without porting TypeScript
module names directly.

## Decisions

- Keep durable lifecycle records in `services/runs`.
- Add `RunSpec` as the persisted executable request shape. It supports
  `ingest` and `garden` first.
- Keep `RunsService` as the owner of queue storage, spec storage, and worker
  lock state.
- Add `RunQueueWorkflow` as the application workflow that drains queued specs
  by calling `IngestWorkflow.run_with_run(...)` or
  `GardenWorkflow.run_with_run(...)`.
- Do not let the CLI shell out to `codealmanac` internally.
- Do not add a second `JobService`. Public CLI noun remains `jobs`; internal
  service noun remains `runs`.
- Keep the process-spawn owner for the next slice. This slice proves the
  in-process execution path and the lock semantics first.

## Shape

```python
queued = app.workflows.queue.queue_ingest(
    RunIngestRequest(cwd=repo, inputs=("note.md",), harness=HarnessKind.CODEX)
)

drained = app.workflows.queue.drain(
    DrainRunQueueRequest(cwd=repo)
)
```

The queue workflow owns operation dispatch:

```python
if item.spec.operation == RunOperation.INGEST:
    ingest.run_with_run(RunIngestWithRunRequest(..., run_id=item.run.run_id))
elif item.spec.operation == RunOperation.GARDEN:
    garden.run_with_run(RunGardenWithRunRequest(..., run_id=item.run.run_id))
```

The run store owns the atomic-ish filesystem details:

```text
<almanac-root>/jobs/<run-id>.json
<almanac-root>/jobs/<run-id>.jsonl
<almanac-root>/jobs/<run-id>.spec.json
<almanac-root>/jobs/worker.lock/owner.json
```

## Cosmic Python Transfer

Chapter 6 frames Unit of Work as the abstraction over atomic operations and
stable persistent state. The filesystem cannot rollback like a database, but
the same lesson applies: queue mutation, spec persistence, lock acquisition,
and terminal finalization need one owned boundary rather than scattered CLI file
writes.

Chapter 4 describes the service layer as the application orchestration layer.
`RunQueueWorkflow` is that layer for queued lifecycle execution; it should call
existing lifecycle workflows instead of knowing prompt, source, or harness
details itself.

Chapter 13 keeps object wiring in the composition root. `app.py` should wire
the queue workflow with `RunsService`, `IngestWorkflow`, and `GardenWorkflow`.

## Files

- `src/codealmanac/services/runs/models.py`
- `src/codealmanac/services/runs/requests.py`
- `src/codealmanac/services/runs/service.py`
- `src/codealmanac/services/runs/store.py`
- `src/codealmanac/workflows/garden/requests.py`
- `src/codealmanac/workflows/garden/service.py`
- `src/codealmanac/workflows/run_queue/`
- `src/codealmanac/app.py`
- `tests/test_runs_service.py`
- `tests/test_run_queue_workflow.py`
- `tests/test_architecture.py`
- steering docs under `docs/python-port/`

## Verification

Run focused checks:

```bash
uv run pytest tests/test_runs_service.py tests/test_run_queue_workflow.py tests/test_architecture.py
uv run ruff check src/codealmanac/services/runs src/codealmanac/workflows src/codealmanac/app.py tests/test_runs_service.py tests/test_run_queue_workflow.py tests/test_architecture.py
```

Then run broad checks:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
