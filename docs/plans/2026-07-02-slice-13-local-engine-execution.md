# Slice 13 Plan: Local Engine Execution

Status: planned.
Date: 2026-07-02.

## Intent

Complete the middle of the local launch pipeline:

```python
prepared = app.workflows.local_runs.prepare_next()
engine = app.workflows.local_engine.execute(run_id, harness)
delivery = app.workflows.local_delivery.deliver(run_id)
```

Slice 13 does not expose a public CLI command. It adds the backend workflow that
cloud and local orchestration can call without going through human CLI strings.

## Product Contract

- The worker receives sources by reference through `sources_path`.
- The model runs inside the prepared worker repo, not the user's active checkout.
- The model may edit only the configured Almanac root.
- The engine writes `~/.codealmanac/runs/<run-id>/result.json`.
- The engine records normalized `run_events` in `~/.codealmanac/control.sqlite`.
- The engine does not commit, merge, open PRs, or deliver changes.
- Delivery remains deterministic and separate.

## Code Shape

```python
result = app.workflows.local_engine.execute(
    ExecuteLocalEngineRunRequest(run_id=run.id, harness=HarnessKind.CODEX)
)
```

Ownership:

- `workflows/local_engine/` owns orchestration for executing a prepared engine
  request.
- `services/engine_runs/` continues to own request/result artifacts.
- `services/harnesses/` continues to own provider-neutral model execution.
- `workflows/local_delivery/` remains the only local writer to the real
  checkout.

## Implementation Scope

Add:

- `src/codealmanac/workflows/local_engine/`
  - `requests.py`
  - `models.py`
  - `prompt.py`
  - `service.py`
  - `__init__.py`
- `src/codealmanac/prompts/operations/update.md`
- `PromptName.OPERATION_UPDATE`
- `app.workflows.local_engine`
- tests for success, failure, and event/result recording

The workflow should:

1. Read the control run and prepared `EngineRunRequest`.
2. Mark the control run `running`.
3. Render an update prompt with the request JSON as runtime context.
4. Run the requested harness with `cwd=request.repo_path`.
5. Append normalized harness events to `run_events`.
6. Write an `EngineRunResult`.
7. Store `result_ref` on the control run.
8. On harness failure, write a failed engine result, mark the run `failed`, and
   append an error event.

## Out Of Scope

- Public CLI command surface.
- Cloud worker execution.
- WorkOS/API/auth changes.
- Delivery changes.
- Parsing a commit subject out of model prose.

## Verification

Focused:

```bash
uv run pytest tests/test_local_engine_workflow.py tests/test_engine_runs_service.py tests/test_architecture.py
```

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
```

## Architecture Notes

The workflow can deterministically derive a commit subject from the harness
summary:

```text
docs almanac: <summary>
```

If no usable summary exists, use:

```text
docs almanac: update wiki
```

The prompt should still instruct the model to produce a concise summary, but
the Python code should not scrape durable fields out of unstructured final
assistant text.
