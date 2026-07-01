# Slice 76 - Background Worker Spawn

Date: 2026-07-01

## Scope

Expose the slice-75 queue core through an actual detached worker path:

- worker spawner port
- subprocess-backed worker spawner adapter
- hidden internal worker CLI command
- explicit `--background` lifecycle mode for `ingest` and `garden`
- JSON/plain output for queued background starts

This slice does **not** change the default mode of `ingest` or `garden`.
Foreground remains default until the product decision is made explicitly.

## Why Now

Slice 75 proved durable specs, queue selection, locks, and in-process drain.
The next missing part of background jobs is the process boundary: enqueue a
spec, spawn a local worker process, and let that process drain through the same
composition root as every other workflow.

The archived behavior defaulted some operations to background. The Python
rewrite should restore the machinery first without silently changing command
defaults in the same slice.

## Decisions

- Keep the worker command internal and hidden as `__run-worker`.
- The CLI is an entrypoint for the child process, not the internal API. The
  hidden command calls `app.workflows.queue.drain(...)`.
- Spawning is an integration adapter behind a service-owned port. Workflows do
  not import `subprocess`.
- Use `sys.executable -m codealmanac.cli.main __run-worker ...` as the child
  command so editable/dev and installed package environments use the same
  Python interpreter.
- Public `ingest --background` and `garden --background` enqueue and spawn.
  Public foreground behavior remains the current default.
- `--json` on background start emits structured run id/status/child pid. It is
  not added as a new foreground result format in this slice.

## Shape

```python
queued = app.workflows.queue.start_ingest_background(
    RunIngestRequest(cwd=repo, inputs=("note.md",), harness=HarnessKind.CODEX)
)

# child process entrypoint
app.workflows.queue.drain(DrainRunQueueRequest(cwd=repo))
```

The worker process is intentionally boring:

```text
python -m codealmanac.cli.main __run-worker --cwd /repo --wiki docs
```

## Cosmic Python Transfer

Chapter 13 names the composition root as the place where dependencies are
wired. `app.py` should inject the subprocess spawner into `RunQueueWorkflow`;
CLI code should not construct the adapter.

Chapter 4 keeps use-case orchestration behind the service/workflow layer. The
hidden worker command should parse args and call `RunQueueWorkflow.drain(...)`;
it must not know how Ingest/Garden work internally.

## Files

- `src/codealmanac/app.py`
- `src/codealmanac/services/runs/ports.py`
- `src/codealmanac/services/runs/requests.py`
- `src/codealmanac/services/runs/models.py`
- `src/codealmanac/integrations/runs/`
- `src/codealmanac/workflows/run_queue/`
- `src/codealmanac/cli/parser/lifecycle.py`
- `src/codealmanac/cli/dispatch/lifecycle.py`
- `src/codealmanac/cli/render/root.py`
- `tests/test_run_queue_workflow.py`
- `tests/test_cli.py`
- `tests/test_architecture.py`

## Verification

Focused:

```bash
uv run pytest tests/test_run_queue_workflow.py tests/test_cli.py tests/test_architecture.py
uv run ruff check src/codealmanac/services/runs src/codealmanac/integrations/runs src/codealmanac/workflows/run_queue src/codealmanac/cli tests/test_run_queue_workflow.py tests/test_cli.py tests/test_architecture.py
```

Broad:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
