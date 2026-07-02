# Slice 36 Cloud Repo Trigger CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Let the terminal mirror the dashboard's maintained-branch trigger settings for the current GitHub checkout.

**Architecture:** Add CLI-owned `repo` commands that resolve the current checkout's GitHub remote, authenticate with the stored cloud CLI token, and call typed `/v1` cloud repository endpoints. The backend `/v1` routes reuse the existing repository service and permission checks; the CLI does not know account IDs or browser session state.

**Tech Stack:** Python argparse CLI, Pydantic models, httpx cloud adapter, FastAPI hosted `/v1` routes, pytest.

---

## Contract

Implemented commands in this slice:

```text
codealmanac repo status
codealmanac repo triggers list
codealmanac repo triggers enable <branch> --delivery pr|commit
codealmanac repo triggers disable <branch>
codealmanac repo delivery set --branch <branch> --mode pr|commit
```

Deferred commands:

```text
codealmanac repo list
codealmanac repo setup
codealmanac repo open
codealmanac repo open settings
codealmanac repo open github
codealmanac repo open github-app
```

Those need dashboard URLs and account/repo browsing decisions. This slice only mirrors the trigger table now present on repository settings.

## Wireframe

```python
checkout = cloud_repo_probe.read(Path.cwd())
state = cloud_auth.require_state(api_url)
repo = cloud_repos.resolve(state, checkout.full_name)
policies = cloud_repos.list_triggers(state, repo.repo_id)

# mutation commands use the same current-checkout resolution
policy = cloud_repos.upsert_trigger(
    state,
    repo.repo_id,
    branch=branch,
    enabled=True,
    delivery_mode="commit",
)
```

Backend `/v1` shape:

```text
POST /v1/repositories/resolve
GET  /v1/repositories/{repo_id}/triggers
PUT  /v1/repositories/{repo_id}/triggers
```

`resolve` accepts `{"fullName": "owner/repo"}` and uses CLI-token auth. Trigger list requires view permission; trigger mutation requires settings permission.

## Task 1: Hosted `/v1` Repository Trigger Routes

**Files:**
- Create: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/server/cli_repositories_router.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/server/app.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/tests/test_cli_repositories_api_contract.py`

Steps:

1. Add a route test for `POST /v1/repositories/resolve` using a fake `repositories.resolve_full_name_for_action`.
2. Add route tests for `GET` and `PUT /v1/repositories/{repo_id}/triggers`.
3. Implement `cli_repositories_router.py` with `current_cli_user`.
4. Register the router in `server/app.py`.
5. Run:
   ```bash
   cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
   uv run pytest tests/test_cli_repositories_api_contract.py tests/test_repositories_api_contract.py -q
   ```

## Task 2: Local CLI Cloud Repository Service

**Files:**
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/services/cloud_repositories/models.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/services/cloud_repositories/requests.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/services/cloud_repositories/ports.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/services/cloud_repositories/service.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/services/cloud_repositories/__init__.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/integrations/cloud/http.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/app.py`
- Test: `/Users/rohan/Desktop/Projects/codealmanac/tests/test_cloud_repositories_service.py`

Steps:

1. Define `CloudRepository`, `CloudRepositoryTriggerPolicy`, and cloud delivery mode models.
2. Define service requests for resolve/list/upsert.
3. Add a `CloudRepositoriesClient` protocol.
4. Implement service methods that require stored CLI auth state and call the client with the token.
5. Extend `HttpCloudAuthClient` with the `/v1` repository methods and response parsers.
6. Wire `cloud_repositories` into `CodeAlmanac`.
7. Run:
   ```bash
   cd /Users/rohan/Desktop/Projects/codealmanac
   uv run pytest tests/test_cloud_repositories_service.py -q
   ```

## Task 3: Current-Checkout Cloud Repo Workflow

**Files:**
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_repo/models.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_repo/requests.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_repo/service.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_repo/__init__.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/app.py`
- Test: `/Users/rohan/Desktop/Projects/codealmanac/tests/test_cloud_repo_workflow.py`

Steps:

1. Reuse the existing Git checkout probe contract for current GitHub remote detection.
2. Add `status`, `list_triggers`, `enable_trigger`, `disable_trigger`, and `set_delivery` workflow methods.
3. Fail clearly when the current directory is not a GitHub checkout.
4. Add workflow tests using fake probe and fake cloud repository service/client.
5. Run:
   ```bash
   cd /Users/rohan/Desktop/Projects/codealmanac
   uv run pytest tests/test_cloud_repo_workflow.py -q
   ```

## Task 4: CLI Parser, Dispatch, And Rendering

**Files:**
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/parser/repo.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/dispatch/repo.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/render/repo.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/parser/admin.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/dispatch/admin.py`
- Test: `/Users/rohan/Desktop/Projects/codealmanac/tests/test_cli.py`

Steps:

1. Add `repo` as a top-level namespace, not `repos`.
2. Add `--api-url` and `--json` where cloud commands need them.
3. Render text rows as `branch<TAB>enabled|disabled<TAB>commit|pr`.
4. Add CLI tests for status, trigger list, enable, disable, and delivery set.
5. Confirm deferred `repo open` and `repo setup` are not silently added.
6. Run:
   ```bash
   cd /Users/rohan/Desktop/Projects/codealmanac
   uv run pytest tests/test_cli.py -q
   ```

## Task 5: Verification And Docs

**Files:**
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/worklog.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/progress.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/verification-matrix.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/next-agent-brief.md`

Commands:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run ruff check .
uv run ruff format --check .
python -m compileall src modal_app -q
uv run pytest tests/test_cli_repositories_api_contract.py tests/test_repositories_api_contract.py -q

cd /Users/rohan/Desktop/Projects/codealmanac
uv run ruff check .
uv run ruff format --check .
python -m compileall src -q
uv run pytest tests/test_cloud_repositories_service.py tests/test_cloud_repo_workflow.py tests/test_cli.py -q
```

Then update launch docs, commit and push both repos, and send a RelayForge milestone update.
