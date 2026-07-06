# Runtime State Home Implementation Plan

**Goal:** Keep committed `almanac/` as source-only Markdown and move derived
runtime state under `~/.codealmanac/repos/<workspace-id>/`.

**Architecture:** Workspace selection still owns repo identity and `almanac/`
source paths. A small runtime-path seam maps a workspace id to local machine
state. Index, runs, and sync ledger stores receive runtime paths explicitly
instead of treating `almanac_path` as both source and state.

Cosmic Python repository rule applied here: keep persistence concerns behind
stores so domain/service code does not know database or ledger file mechanics.
See `docs/reference/cosmic-python/chapter_02_repository.md`.

## Runtime Shape

```text
~/.codealmanac/
|-- registry.json
|-- config.toml
`-- repos/
    `-- <workspace-id>/
        |-- index.db
        |-- index.db-wal
        |-- index.db-shm
        `-- runs/
            |-- <run-id>.json
            |-- <run-id>.jsonl
            |-- <run-id>.spec.json
            |-- sync-ledger.json
            `-- worker.lock/
                `-- owner.json
```

In tests, `AppConfig(registry_path=<tmp>/.codealmanac/registry.json)` makes
`<tmp>/.codealmanac/` the runtime state root.

## Task 1: Add Runtime Path Seam

Files:

- Create `src/codealmanac/services/workspaces/runtime.py`
- Modify `src/codealmanac/app.py`
- Modify `src/codealmanac/services/workspaces/models.py` only if the runtime
  path should be exposed on `Workspace`

Steps:

1. Add `WorkspaceRuntimePaths.repo_dir(workspace)` as the single mapping from
   workspace identity to runtime directory.
2. Instantiate it from `app_config.registry_path.parent`.
3. Inject it into services that need runtime state.

## Task 2: Move The Index DB

Files:

- `src/codealmanac/services/index/service.py`
- `src/codealmanac/services/index/store.py`
- `src/codealmanac/services/index/schema.py`
- `tests/test_read_model.py`
- `tests/test_cli.py`
- `tests/test_build_workflow.py`

Steps:

1. Change `index_db_path` to accept a repo runtime directory.
2. Keep page loading from `workspace.almanac_path`.
3. Run all index reads against `runtime/index.db`.
4. Update stale-schema and refresh tests to inspect the runtime DB.

## Task 3: Move Run Records, Logs, Specs, Locks

Files:

- `src/codealmanac/services/runs/service.py`
- `src/codealmanac/services/runs/store.py`
- `src/codealmanac/services/runs/paths.py`
- `src/codealmanac/services/runs/io.py`
- `src/codealmanac/services/runs/locks.py`
- `src/codealmanac/services/runs/transitions.py`
- `src/codealmanac/services/runs/queries.py`
- `src/codealmanac/services/runs/factory.py`
- `tests/test_runs_service.py`
- `tests/test_run_queue_workflow.py`
- `tests/test_cli.py`

Steps:

1. Rename store/path arguments from `almanac_path` to `runtime_path`.
2. Store run files under `<runtime>/runs/`.
3. Keep public `RunRecord.log_path` as a readable runtime-relative path:
   `runs/<run-id>.jsonl`.
4. Update worker lock tests to assert locks live under runtime.

## Task 4: Move Sync Ledger

Files:

- `src/codealmanac/workflows/sync/store.py`
- `src/codealmanac/workflows/sync/evaluation.py`
- `src/codealmanac/workflows/sync/execution.py`
- `tests/test_sync_workflow.py`
- `tests/test_cli.py`

Steps:

1. Store `sync-ledger.json` under `<runtime>/runs/`.
2. Thread runtime paths into sync evaluation/execution through workspace lookup.
3. Keep transcript candidates tied to source `almanac_path`; only ledger IO
   moves.

## Task 5: Remove Repo Gitignore Runtime Entries

Files:

- `src/codealmanac/services/wiki/templates.py`
- `src/codealmanac/services/wiki/service.py`
- `tests/test_build_workflow.py`
- `tests/test_public_contract.py`
- `README.md`
- `almanac/architecture/indexing.md`
- `almanac/architecture/lifecycle-runs.md`

Steps:

1. Stop adding `almanac/index.db` and `almanac/jobs/` to repo `.gitignore`.
2. Keep existing user `.gitignore` content untouched.
3. Update docs to state runtime state is outside the repo.

## Verification

```bash
uv run pytest tests/test_read_model.py tests/test_runs_service.py tests/test_run_queue_workflow.py tests/test_sync_workflow.py tests/test_cli.py tests/test_build_workflow.py tests/test_public_contract.py tests/test_viewer_service.py
uv run pytest
uv run ruff check .
tmp_home=$(mktemp -d)
HOME="$tmp_home" uv run codealmanac health
find almanac -name index.db -o -path 'almanac/jobs/*'
```

Expected:

- `almanac/` contains only source wiki files.
- Index DB, run files, worker locks, and sync ledger live under runtime.
- Missing runtime state rebuilds from Markdown source.
- No init/build path writes runtime ignore entries into repo `.gitignore`.
