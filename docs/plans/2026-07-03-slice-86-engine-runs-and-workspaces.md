# Slice 86: Engine Runs And Workspaces

## Goal

Finish the next local-side naming cleanup after Slice 85 by moving engine-owned
runtime artifacts and workspaces into engine-owned packages:

```text
local/runs/artifacts      -> engine/runs
engine/worker_workspaces  -> engine/workspaces
app.engine.runs           -> app.engine.runs
app.engine.workspaces     -> app.engine.workspaces
```

`local/runs/` should keep branch-triggered local orchestration. The model
worker request/result files and detached worktree layout are engine
infrastructure, not local control-plane concepts.

## Scope

- Move `src/codealmanac/local/runs/artifacts/` to
  `src/codealmanac/engine/runs/`.
- Move `src/codealmanac/engine/worker_workspaces/` to
  `src/codealmanac/engine/workspaces/`.
- Rename workspace types from worker-specific names to engine workspace names:
  `WorkerWorkspacePaths` -> `EngineWorkspacePaths`,
  `PreparedEngineWorkspace` -> `PreparedEngineWorkspace`,
  `EngineWorkspacesService` -> `EngineWorkspacesService`, and matching request
  and store names.
- Add a `CodeAlmanacEngine` composition-root facade so callers can use
  `app.engine.runs` and `app.engine.workspaces`.
- Update local run preparation, local engine execution, delivery, integrations,
  CLI tests, and architecture tests.
- Update launch/refactor docs with the new hierarchy.

## Out Of Scope

- Moving root packaged `prompts/` or `manual/`.
- Hosted `codealmanac-hosted` package/domain refactors.
- Changing public CLI commands or local DB table names.
- Renaming branch-triggered `local/runs/` or cloud `runs/`.

## Design

The intended call shape is:

```python
engine = CodeAlmanacEngine(
    harnesses=harnesses,
    sources=sources,
    source_bundles=source_bundles,
    runs=engine_runs,
    workspaces=engine_workspaces,
)

local_runs = LocalRunPreparationWorkflow(
    control=control,
    engine_workspaces=engine.workspaces,
    source_bundles=engine.source_bundles,
    engine_runs=engine.runs,
)
```

This follows the Cosmic Python repository/service split: stores own artifact
paths and JSON persistence, services own product verbs, and `app.py` remains
the composition root.

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `docs/python-port-live-agreement.md`
- `docs/reference/cosmic-python/chapter_02_repository.md`
- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_10_commands.md`
- `docs/reference/cosmic-python/chapter_13_dependency_injection.md`

## Verification

Focused:

```bash
uv run pytest \
  tests/test_engine_runs_service.py \
  tests/test_engine_workspaces_service.py \
  tests/test_local_run_preparation_workflow.py \
  tests/test_local_engine_workflow.py \
  tests/test_local_delivery_workflow.py \
  tests/test_local_worker_workflow.py \
  tests/test_cli.py \
  tests/test_architecture.py \
  -q --tb=short
```

Full:

```bash
uv run ruff check src tests
uv run pytest -q --tb=short
git diff --check
```

## Result

- Moved engine run artifacts from `src/codealmanac/local/runs/artifacts/` to
  `src/codealmanac/engine/runs/`.
- Moved detached engine workspace management from
  `src/codealmanac/engine/worker_workspaces/` to
  `src/codealmanac/engine/workspaces/`.
- Added the `CodeAlmanacEngine` composition-root facade and wired local run
  preparation, execution, and delivery through `app.engine.runs` and
  `app.engine.workspaces`.
- Renamed the local preparation result field from `worker_workspace` to
  `engine_workspace`.
- Focused verification passed:

```bash
uv run pytest tests/test_engine_runs_service.py tests/test_engine_workspaces_service.py tests/test_local_run_preparation_workflow.py tests/test_local_worker_workflow.py tests/test_local_delivery_workflow.py tests/test_local_engine_workflow.py tests/test_architecture.py -q --tb=short
```

Result: `96 passed`.

Full verification passed:

```bash
uv run ruff check src tests
uv run pytest -q --tb=short
git diff --check
```

Result: `ruff` passed, `514 passed`, and diff check passed.
