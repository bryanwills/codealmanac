# Slice 24 User-Level Jobs State Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move file-backed lifecycle job state from repo-local Almanac roots to
user-level CodeAlmanac state while preserving read compatibility for legacy
repo-local job files.

**Architecture:** Add a first-class `jobs_path` to `AppConfig` with default
`~/.codealmanac/jobs`. `RunsService` maps each workspace to
`<jobs_path>/<workspace-id>/` for new run records, logs, specs, and worker
locks. `SyncLedgerStore` uses the same workspace job directory for
`sync-ledger.json`. Legacy `<almanac-root>/jobs/` files remain readable so
older local state does not disappear during the transition.

**Tech Stack:** Python, pathlib, Pydantic config models, file-backed run store,
sync ledger store, pytest.

**Status:** Implemented and verified on 2026-07-02.

---

## Scope

- Add `AppConfig.jobs_path`, defaulting to `~/.codealmanac/jobs`.
- New file-backed lifecycle jobs write to:

  ```text
  ~/.codealmanac/jobs/<workspace-id>/<run-id>.json
  ~/.codealmanac/jobs/<workspace-id>/<run-id>.jsonl
  ~/.codealmanac/jobs/<workspace-id>/<run-id>.spec.json
  ~/.codealmanac/jobs/<workspace-id>/worker.lock/
  ~/.codealmanac/jobs/<workspace-id>/sync-ledger.json
  ```

- `RunsService` lists, shows, logs, attaches, cancels, and transitions legacy
  repo-local runs when those run ids only exist under
  `<almanac-root>/jobs/`.
- New run writes, queue specs, and worker locks use the user-level jobs root.
- `SyncLedgerStore` reads a legacy repo-local `sync-ledger.json` only when no
  user-level ledger exists, and writes subsequent ledger state to the
  user-level jobs root.
- README, manual, starter docs, and launch storage docs stop teaching
  `<almanac-root>/jobs/` as the active runtime location.

## Out Of Scope

- Migrating old files on disk.
- Deleting legacy `<almanac-root>/jobs/`.
- Moving query/index files out of the repo-local Almanac root.
- Changing SQL-backed local control runs or engine artifacts.
- Changing cloud storage.

## Design

```python
app_config.jobs_path == Path.home() / ".codealmanac/jobs"

workspace = workspaces.resolve(cwd)
primary_jobs = jobs_path / workspace.workspace_id
legacy_jobs = workspace.almanac_path / "jobs"

# new writes
runs.start(...) -> primary_jobs/<run>.json + primary_jobs/<run>.jsonl
runs.queue(...) -> primary_jobs/<run>.spec.json
sync.ledger.save(...) -> primary_jobs/sync-ledger.json

# read bridge
runs.show(run_id) -> primary first, legacy fallback
runs.log(run_id) -> same location as the found record
runs.list(...) -> primary + legacy, primary wins on duplicate run_id
sync.ledger.load(...) -> primary first, legacy fallback
```

The run store itself should stop pretending its directory argument is an
Almanac path. It owns a run ledger directory. `RunsService` owns workspace
resolution and path selection.

## Files

Modify:

- `src/codealmanac/core/paths.py`
- `src/codealmanac/core/models.py`
- `src/codealmanac/app.py`
- `src/codealmanac/services/runs/paths.py`
- `src/codealmanac/services/runs/factory.py`
- `src/codealmanac/services/runs/io.py`
- `src/codealmanac/services/runs/locks.py`
- `src/codealmanac/services/runs/queries.py`
- `src/codealmanac/services/runs/service.py`
- `src/codealmanac/services/runs/store.py`
- `src/codealmanac/services/runs/streaming.py`, only if naming needs cleanup
- `src/codealmanac/workflows/sync/evaluation.py`
- `src/codealmanac/workflows/sync/execution.py`
- `src/codealmanac/workflows/sync/store.py`
- `src/codealmanac/services/wiki/templates.py`
- `src/codealmanac/manual/README.md`
- `README.md`
- `tests/test_runs_service.py`
- `tests/test_run_queue_workflow.py`
- `tests/test_cli.py`
- `tests/test_sync_workflow.py`
- `tests/test_public_contract.py`
- `tests/test_architecture.py`
- `docs/codealmanac-launch/schema-contract.md`
- `docs/codealmanac-launch/verification-matrix.md`
- `docs/codealmanac-launch/progress.md`
- `docs/codealmanac-launch/worklog.md`
- `docs/codealmanac-launch/next-agent-brief.md`

## Tests

Focused:

```bash
uv run pytest tests/test_runs_service.py tests/test_run_queue_workflow.py tests/test_sync_workflow.py tests/test_cli.py tests/test_public_contract.py tests/test_architecture.py
```

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
uv run codealmanac --help
```

## Implementation Tasks

1. Add `default_jobs_path()` and `AppConfig.jobs_path`.
2. Rename run-store path helpers from Almanac-root assumptions to run-ledger
   directory assumptions.
3. Change `RunStore.create(...)` and `RunStore.queue(...)` to accept a run
   ledger directory and log reference directory.
4. Add `RunsService` path selection:
   primary user-level jobs directory, legacy repo-local jobs directory, and
   helper methods that find the directory for an existing run id.
5. Make `list`, `show`, `log`, `attach`, `stream_attach`, `read_spec`,
   `mark_running`, `append`, `record_harness_transcript`, `finish`, and
   `cancel` use the selected run directory.
6. Keep new `start`, `queue`, `next_queued`, and `acquire_worker_lock` pointed
   at the primary user-level jobs directory, while `next_queued` can fall back
   to legacy queued specs when no primary queued spec exists.
7. Change `SyncLedgerStore` to load/save by repo root plus Almanac path, using
   `workspace_id_for(repo_root)` to select the user-level jobs directory and
   legacy read fallback.
8. Update sync evaluator/executor call sites and tests.
9. Update README/manual/starter docs and launch storage docs.
10. Run focused tests, full tests, ruff, diff check, commit, push, send
    RelayForge, and record the bookkeeping update.

## Verification

```bash
uv run pytest tests/test_runs_service.py tests/test_run_queue_workflow.py tests/test_sync_workflow.py tests/test_cli.py tests/test_public_contract.py tests/test_architecture.py -q
uv run pytest
uv run ruff check .
git diff --check
uv run codealmanac --help
uv run codealmanac dev ingest --help
uv run codealmanac dev garden --help
```

Focused gate: `181 passed`.

Full gate: `466 passed`.
