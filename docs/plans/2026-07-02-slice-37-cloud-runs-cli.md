# Cloud Runs CLI Mirrors Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add read-only cloud run inspection from the terminal: `codealmanac runs list`, `codealmanac runs show <run-id>`, and `codealmanac runs logs <run-id>`.

**Architecture:** Keep local execution under `jobs`; add a separate cloud `runs` path that uses the stored CLI token and current GitHub checkout to resolve the cloud repository. Hosted adds CLI-token `/v1` run read routes that mirror existing browser `/api` run routes without account-scoped URL parameters.

**Tech Stack:** FastAPI, Pydantic DTOs, SQL-backed hosted `Updates` service, CodeAlmanac Python services/workflows, argparse CLI, pytest.

---

## Scope

Implement now:

- Hosted `/v1/repositories/{repo_id}/runs`
- Hosted `/v1/runs/{run_id}`
- Hosted `/v1/runs/{run_id}/events`
- CodeAlmanac `cloud_runs` service and HTTP adapter methods
- CodeAlmanac `cloud_runs` workflow that resolves the current checkout through the same local Git probe as `repo status`
- CLI:
  - `codealmanac runs list [--limit N] [--json]`
  - `codealmanac runs show <run-id> [--json]`
  - `codealmanac runs logs <run-id> [--json]`

Defer:

- `codealmanac runs start`
- `codealmanac runs cancel`
- `codealmanac runs retry`
- Browser UI changes
- Worker lifecycle changes

Reason for deferral: read-only inspection uses existing service semantics. Start/cancel/retry need explicit queue, billing, GitHub check, and worker-state semantics.

## Design Wireframe

```python
# Hosted route edge
user = current_cli_user(token)
page = almanac.updates.runs_for_repo(user, repo_id, PageRequest(...))
run = almanac.updates.run_for_user(user, run_id)
events = almanac.updates.run_events_for_user(user, run_id)

# CodeAlmanac package API
repo_status = app.workflows.cloud_repo.status(...)
runs = app.cloud_runs.list_for_repo(repo_status.repository.repo_id)
run = app.cloud_runs.show(run_id)
events = app.cloud_runs.events(run_id)

# CLI edge
codealmanac runs list
codealmanac runs show <run-id>
codealmanac runs logs <run-id>
```

## Task 1: Hosted CLI Run Routes

**Files:**

- Create: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/server/cli_runs_router.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/server/app.py`
- Test: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/tests/test_cli_runs_api_contract.py`

**Steps:**

1. Add tests proving `/v1/repositories/{repo_id}/runs`, `/v1/runs/{run_id}`, and `/v1/runs/{run_id}/events` authenticate through `cli_tokens.authenticate`.
2. Implement `cli_runs_router.py` with `current_cli_user` and existing `RunDTO`, `RunEventDTO`, and `PageDTO`.
3. Include the router in `server/app.py`.
4. Run:
   ```bash
   cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
   uv run pytest tests/test_cli_runs_api_contract.py tests/test_repositories_api_contract.py tests/test_updates_contract.py -q
   ```

Expected: all pass.

## Task 2: CodeAlmanac Cloud Runs Service

**Files:**

- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/services/cloud_runs/models.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/services/cloud_runs/ports.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/services/cloud_runs/requests.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/services/cloud_runs/service.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/services/cloud_runs/__init__.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/integrations/cloud/http.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/app.py`
- Test: `/Users/rohan/Desktop/Projects/codealmanac/tests/test_cloud_runs_service.py`

**Steps:**

1. Add Pydantic models for cloud run source, run, event, and paged list.
2. Add a service-owned `CloudRunsClient` protocol.
3. Add request objects for list/show/events.
4. Add HTTP adapter parsing for hosted run DTOs.
5. Wire `CloudRunsService` in `create_app`.
6. Run:
   ```bash
   cd /Users/rohan/Desktop/Projects/codealmanac
   uv run pytest tests/test_cloud_runs_service.py -q
   ```

Expected: pass.

## Task 3: CodeAlmanac Cloud Runs Workflow And CLI

**Files:**

- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_runs/models.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_runs/requests.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_runs/service.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_runs/__init__.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/parser/runs.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/dispatch/runs.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/render/cloud_runs.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/parser/admin.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/dispatch/admin.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/render/admin.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/tests/test_cli.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/tests/test_architecture.py`
- Test: `/Users/rohan/Desktop/Projects/codealmanac/tests/test_cloud_runs_workflow.py`

**Steps:**

1. Add a workflow that resolves current checkout through `CloudRepoWorkflow.status`.
2. Add `runs list/show/logs` parsing with `--api-url` and `--json`.
3. Render tabular rows for human output and typed JSON for `--json`.
4. Add CLI tests using a fake cloud runs client.
5. Add architecture tests so parser/dispatch/render packages remain split.
6. Run:
   ```bash
   cd /Users/rohan/Desktop/Projects/codealmanac
   uv run pytest tests/test_cloud_runs_service.py tests/test_cloud_runs_workflow.py tests/test_cli.py tests/test_architecture.py -q
   ```

Expected: pass.

## Task 4: Docs, Verification, Commit, Push

**Files:**

- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/auth-api-contract.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/cli-contract.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/progress.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/verification-matrix.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/worklog.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/next-agent-brief.md`

**Verification:**

Hosted:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_cli_runs_api_contract.py tests/test_repositories_api_contract.py tests/test_updates_contract.py -q
uv run ruff check .
uv run python -m compileall src modal_app -q
```

CodeAlmanac:

```bash
cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest tests/test_cloud_runs_service.py tests/test_cloud_runs_workflow.py tests/test_cli.py tests/test_architecture.py -q
uv run ruff check .
uv run python -m compileall src -q
git diff --check
```

Commit/push:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence
git commit -m "feat: add CLI run read routes"
git push origin codex/workos-authkit-api-foundation

cd /Users/rohan/Desktop/Projects/codealmanac
git commit -m "feat: inspect cloud runs from CLI"
git push origin dev
```
