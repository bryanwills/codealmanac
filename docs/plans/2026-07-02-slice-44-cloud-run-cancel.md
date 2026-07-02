# Slice 44: Cloud Run Cancellation

## Goal

Add real cancellation for hosted update runs and expose it through the
CodeAlmanac CLI.

The public command is:

```bash
codealmanac runs cancel <run-id>
```

The command is cloud-first, authenticated by the stored CLI token, and does not
depend on the current checkout. The backend authorizes the user through the
run's repository.

## Why This Slice

Cloud runs can now be listed, shown, logged, and manually started. Users also
need a way to stop a queued or running cloud update from the terminal. Modal's
Python SDK exposes `FunctionCall.from_id(call_id).cancel(...)`, so cancellation
can be a real provider action instead of a cosmetic status change.

Retry is intentionally not included. Retry needs a separate source-head policy:
failed/stale retry could reuse the original source, refresh the current branch
head, or create a new manual branch run. That decision should be explicit.

## Product Contract

- `queued` -> `cancelled` without contacting Modal.
- `running` with `worker_call_id` -> call Modal cancel, then mark
  `cancelled`.
- `cancelled` -> return the existing run unchanged.
- `delivered`, `failed`, and `stale` -> 409 conflict.
- `running` without `worker_call_id` -> 409 conflict because there is no
  provider handle to cancel.
- Cancellation writes a `status` run event with message `cancelled`.
- Cancellation dispatches a terminal `RunCancelled` event after commit.
- GitHub Checks fanout publishes conclusion `cancelled` for `RunCancelled`.
- Browser API and CLI API both expose cancellation because browser and CLI
  should be mirrors over the same product verb.

## Architecture

```python
run = almanac.updates.cancel_run(user, run_id)

# service-owned product verb
UpdateCancellation.cancel(user, run_id)
  run = store.get(..., for_update=True)
  repositories.authorize(user, run.repo_id, Action.APPROVE_UPDATE)
  if run.status == QUEUED:
      cancelled = store.mark_cancelled(...)
  if run.status == RUNNING:
      workers.cancel(run)
      cancelled = store.mark_cancelled(...)
  events.dispatch([RunCancelled(...)], session=session)
```

Modal remains an integration detail:

```python
UpdateWorkers.cancel(run)
  worker.cancel(run.worker_call_id)

ModalWorker.cancel(call_id)
  modal.FunctionCall.from_id(call_id).cancel(terminate_containers=False)
```

Use `terminate_containers=False` first. It cancels the function call without
forcibly killing shared containers. We can add a separate force-cancel flag only
if provider behavior shows stuck runs in practice.

## Hosted Files

- `backend/src/almanac/services/updates/models.py`
- `backend/src/almanac/services/updates/store.py`
- `backend/src/almanac/services/updates/workers.py`
- `backend/src/almanac/services/updates/cancellation.py`
- `backend/src/almanac/services/updates/service.py`
- `backend/src/almanac/services/events/models.py`
- `backend/src/almanac/integrations/modal/client.py`
- `backend/src/almanac/server/dtos/runs.py`
- `backend/src/almanac/server/cli_runs_router.py`
- `backend/src/almanac/server/runs_router.py`
- `backend/src/almanac/wiring/fanout/github_checks.py`

## CodeAlmanac Files

- `src/codealmanac/services/cloud_runs/models.py`
- `src/codealmanac/services/cloud_runs/ports.py`
- `src/codealmanac/services/cloud_runs/requests.py`
- `src/codealmanac/services/cloud_runs/service.py`
- `src/codealmanac/integrations/cloud/http.py`
- `src/codealmanac/workflows/cloud_runs/requests.py`
- `src/codealmanac/workflows/cloud_runs/service.py`
- `src/codealmanac/cli/parser/runs.py`
- `src/codealmanac/cli/dispatch/runs.py`

## Tests

Hosted focused tests:

```bash
uv run pytest \
  tests/test_updates_contract.py \
  tests/test_cli_runs_api_contract.py \
  tests/test_github_checks_fanout.py \
  tests/test_events_contract.py \
  tests/test_modal_worker_contract.py \
  -q
```

CodeAlmanac focused tests:

```bash
uv run pytest \
  tests/test_cloud_runs_service.py \
  tests/test_cloud_runs_workflow.py \
  tests/test_cli.py \
  tests/test_architecture.py \
  -q
```

Full gates after focused tests:

```bash
# hosted backend
uv run pytest -q
uv run ruff check .
uv run python -m compileall src modal_app -q
git diff --check

# codealmanac
uv run pytest -q
uv run ruff check .
uv run python -m compileall src -q
git diff --check
```

## Done

- `RunStatus.CANCELLED` is accepted everywhere `RunDTO` and cloud CLI models
  parse run status.
- `POST /v1/runs/{run_id}/cancel` and `POST /api/runs/{run_id}/cancel` return
  the cancelled run.
- `codealmanac runs cancel <run-id>` returns the run detail.
- Running cancellation calls the Modal provider through a typed integration
  method.
- Terminal cancellation publishes a GitHub Check conclusion of `cancelled`.
- Launch docs and progress are updated before commit.
