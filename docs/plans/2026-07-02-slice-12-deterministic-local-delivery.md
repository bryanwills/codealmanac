# Slice 12: Deterministic Local Delivery

Date: 2026-07-02.
Status: planned.

## Goal

Deliver a completed local worker repo back to the user's real checkout
deterministically. The agent/model writes wiki files in the detached worker
repo; delivery code validates, applies, and commits the wiki diff.

## Architecture

```python
result = app.workflows.local_delivery.deliver(run_id)

run       = control.get_run(run_id)
repo      = control.get_repository(run.repository_id)
branch    = control.get_branch(run.branch_id)
engine    = engine_runs.read_result(run_id)
delivery  = deliveries.create(run, branch.delivery_mode)

head = git_delivery.read_head(repo.local_root_path)
if head != run.expected_head_sha:
    mark run stale
    mark delivery skipped

patch = git_delivery.collect_patch(worker_repo, repo.almanac_root)
if patch.empty:
    mark run succeeded
    mark delivery skipped

commit = git_delivery.apply_patch_and_commit(
    repo.local_root_path,
    repo.almanac_root,
    patch,
    engine.commit_subject,
    engine.commit_body,
)
mark run succeeded
mark delivery succeeded
```

## Scope

- Add a delivery ledger service over the existing `deliveries` table.
- Add local delivery workflow and typed result models.
- Add a Git delivery port and concrete native-Git implementation.
- Add worker workspace path lookup so delivery can find the detached worker
  repo for a run.
- Support local `commit` delivery mode.
- Mark moved-head deliveries as skipped and runs as `stale`.
- Mark no-op wiki diffs as skipped and runs as `succeeded`.
- Commit with the `docs almanac:` subject style from the engine result.

## Out Of Scope

- PR delivery.
- Working-tree delivery mode.
- Cloud delivery through GitHub APIs.
- Running the model/engine.
- Starting a replacement trigger when the branch moved.

## Boundary Rules

- Workflow owns orchestration.
- `services/deliveries` owns delivery rows.
- Git command mechanics live only in `integrations/workspaces/git/delivery.py`.
- The workflow must not call the human CLI.
- The Git integration must reject worker changes outside `almanac_root`.
- Delivery must check the real checkout head before applying a patch.

## Files

Create:

- `src/codealmanac/services/deliveries/`
- `src/codealmanac/workflows/local_delivery/`
- `src/codealmanac/integrations/workspaces/git/delivery.py`
- `tests/test_deliveries_service.py`
- `tests/test_local_delivery_workflow.py`
- `tests/test_git_local_delivery.py`

Modify:

- `src/codealmanac/app.py`
- `src/codealmanac/services/control/records.py`
- `src/codealmanac/services/worker_workspaces/requests.py`
- `src/codealmanac/services/worker_workspaces/service.py`
- `tests/test_architecture.py`
- launch docs under `docs/codealmanac-launch/`

## Verification

Focused:

```text
uv run pytest tests/test_deliveries_service.py tests/test_local_delivery_workflow.py tests/test_git_local_delivery.py tests/test_worker_workspaces_service.py tests/test_architecture.py
```

Full:

```text
uv run pytest
uv run ruff check .
git diff --check
```
