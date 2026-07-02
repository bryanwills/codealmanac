# Slice 14 Plan: Local Worker Orchestration

Status: planned.
Date: 2026-07-02.

## Intent

Add the local worker workflow that runs one pending branch-triggered update:

```python
result = app.workflows.local_worker.run_next(
    RunNextLocalWorkerRequest(harness=HarnessKind.CODEX)
)
```

This is the first single-call backend path for the local trigger pipeline.

## Product Contract

- Local hooks record trigger events.
- The local worker claims one pending trigger and creates one control run.
- Preparation creates the worker repo, source bundle, and engine request.
- Engine execution runs the model in the worker repo.
- Delivery is attempted only after a successful engine result.
- Delivery is skipped if the run was marked `stale` while the engine was
  running.
- The worker returns a typed result instead of throwing for normal no-op or
  failed-run outcomes.

## Code Shape

```python
worker = app.workflows.local_worker.run_next(request)

worker.preparation  # local_runs.prepare_next(...)
worker.engine       # local_engine.execute(...)
worker.delivery     # local_delivery.deliver(...), if still deliverable
worker.run          # final control run record when one exists
```

Ownership:

- `workflows/local_worker/` owns the local end-to-end orchestration.
- `workflows/local_runs/` still owns claim and preparation.
- `workflows/local_engine/` still owns model execution.
- `workflows/local_delivery/` still owns deterministic delivery.

## Implementation Scope

Add:

- `src/codealmanac/workflows/local_worker/`
  - `requests.py`
  - `models.py`
  - `service.py`
  - `__init__.py`
- `app.workflows.local_worker`
- tests for no pending trigger, successful full path, preparation failure, and
  engine failure
- architecture guard that the local worker only composes workflows

The workflow should:

1. Call `local_runs.prepare_next(...)`.
2. Return a no-op result when no pending trigger exists.
3. Return a processed failed result when preparation claimed a run but failed.
4. Call `local_engine.execute(...)` for prepared runs.
5. Skip delivery if engine execution fails.
6. Skip delivery if the control run is no longer `running` after engine
   execution.
7. Call `local_delivery.deliver(...)` for successful, still-running runs.

## Out Of Scope

- Public CLI command.
- Background subprocess worker.
- Hook block changes.
- Cloud worker implementation.
- Retry policy.
- Cross-repo parallel worker locking beyond the existing atomic trigger claim
  and stale-run behavior.

## Verification

Focused:

```bash
uv run pytest tests/test_local_worker_workflow.py tests/test_local_run_preparation_workflow.py tests/test_local_engine_workflow.py tests/test_local_delivery_workflow.py tests/test_architecture.py
```

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
