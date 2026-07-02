# Slice 22 Init Runtime Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make `codealmanac init` the public first-build lifecycle command and remove public `codealmanac build`.

**Architecture:** Add an `InitWorkflow` that owns workspace scaffolding plus agent-backed first-build runs. Reuse `PageRunWorkflow` for run state, harness execution, transcript/event capture, mutation validation, and index refresh. Keep `ingest` and `garden` behavior unchanged.

**Tech Stack:** Python, argparse, Pydantic request/result models, file-backed run store, shared harness/page-run workflow, pytest.

**Status:** Implemented on 2026-07-02.

---

## Scope

- Public `codealmanac init` supports:
  `--root`, `--name`, `--description`, `--using`, `--background`,
  `--foreground`, `--force`, `--yes`, `--verbose`, and `--json`.
- Public `codealmanac build` is removed from the parser and lifecycle dispatch.
- `RunOperation.INIT` replaces the old `RunOperation.BUILD` lifecycle word.
- `RunSpec` can persist queued init jobs.
- `RunQueueWorkflow.queue_init(...)` and `start_init_background(...)` exist.
- `__run-worker` can drain queued init specs.
- Diagnostics, starter text, CLI tests, and architecture tests stop teaching
  `codealmanac build`.

## Out Of Scope

- Hiding public `ingest` and `garden`.
- Cloud setup/API work.
- Moving repo-local run files to the local control DB.
- Real live harness dogfood with Codex against this repo.

## Design

```python
app.workflows.init.initialize_workspace(InitializeWorkspaceRequest(...))

result = app.workflows.init.run(
    RunInitRequest(
        path=repo,
        harness=HarnessKind.CODEX,
        force=True,
        guidance=None,
    )
)

queued = app.workflows.queue.start_init_background(...)
drain = app.workflows.queue.drain(...)
```

`initialize_workspace(...)` is scaffold-only for tests, setup, and other
workflows that need an initialized wiki before exercising another command.

`run(...)` is the public first-build path:

1. Resolve the initialization target.
2. Count pages that existed before scaffolding.
3. Refuse populated wikis unless `force=True`.
4. Register the workspace.
5. Create starter wiki/manual files if missing.
6. Start a `RunOperation.INIT` run.
7. Run the init prompt through `PageRunWorkflow`.
8. Render the same run/log/index evidence style as ingest and garden.

`init` uses a page-run mutation policy that allows pre-existing Almanac-root
changes because init itself creates the root before the agent runs. The policy
still rejects reported or actual changes outside the configured Almanac root.

## Files

Create:

- `src/codealmanac/workflows/init/__init__.py`
- `src/codealmanac/workflows/init/models.py`
- `src/codealmanac/workflows/init/requests.py`
- `src/codealmanac/workflows/init/service.py`
- `src/codealmanac/cli/dispatch/init.py`
- `tests/test_init_workflow.py`

Modify:

- `src/codealmanac/app.py`
- `src/codealmanac/cli/parser/lifecycle.py`
- `src/codealmanac/cli/dispatch/lifecycle.py`
- `src/codealmanac/cli/render/lifecycle.py`
- `src/codealmanac/cli/render/root.py`
- `src/codealmanac/services/runs/models.py`
- `src/codealmanac/workflows/run_queue/service.py`
- `src/codealmanac/workflows/lifecycle_mutation.py`
- `src/codealmanac/workflows/page_run/service.py`
- `src/codealmanac/services/diagnostics/wiki.py`
- `src/codealmanac/services/wiki/templates.py`
- `tests/test_cli.py`
- `tests/test_diagnostics.py`
- `tests/test_run_queue_workflow.py`
- `tests/test_architecture.py`
- call sites that use `app.workflows.build.initialize(...)`

Delete:

- `src/codealmanac/cli/dispatch/build.py`
- `src/codealmanac/workflows/build/models.py`
- `src/codealmanac/workflows/build/service.py`
- `src/codealmanac/workflows/build/__init__.py`

## Tests

Focused:

```bash
uv run pytest tests/test_init_workflow.py tests/test_cli.py tests/test_diagnostics.py tests/test_run_queue_workflow.py tests/test_architecture.py
```

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
uv run codealmanac --help
uv run codealmanac init --help
```

## Implementation Tasks

1. Add init request/result models and service.
2. Add init mutation-policy support in `LifecycleMutationPolicy`.
3. Wire `InitWorkflow` in `app.py`.
4. Replace public parser/dispatch/render build paths with init paths.
5. Extend `RunOperation`, `RunSpec`, and `RunQueueWorkflow` for init.
6. Update diagnostics and starter README fixes from `build` to `init`.
7. Mechanically migrate scaffold-only test setup from `workflows.build` to
   `workflows.init.initialize_workspace`.
8. Add focused tests for foreground init, populated-wiki refusal, `--force`,
   background queueing/draining, parser build removal, and diagnostics text.
9. Update launch-folder evidence and progress after verification.

## Verification Performed

```bash
uv run pytest tests/test_init_workflow.py tests/test_cli.py tests/test_diagnostics.py tests/test_run_queue_workflow.py tests/test_runs_service.py tests/test_build_workflow.py tests/test_architecture.py
# 158 passed

uv run pytest
# 465 passed

uv run ruff check .
git diff --check
uv run codealmanac --help
uv run codealmanac init --help
```
