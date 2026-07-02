# Slice 31 Hosted Direct Maintenance API Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the hosted Modal worker's CodeAlmanac subprocess bridge with a typed Python maintenance API call.

**Architecture:** CodeAlmanac exposes a narrow `codealmanac.maintenance` package API over the existing init and ingest workflows. The hosted worker lazily imports that API inside Modal, builds a typed maintenance request from the hosted `Run`, and calls it directly. The human CLI remains a separate edge over the same workflows; hosted code no longer constructs public CLI commands for worker execution.

**Tech Stack:** Python 3.12, Pydantic request/result models, CodeAlmanac workflow services, Modal worker modules, pytest, Ruff.

**Status:** Planned on 2026-07-02.

---

## Decisions

- Do not name the new package `sdk`; the current public package contract
  explicitly forbids top-level `sdk` and `mcp` modules.
- Use `codealmanac.maintenance` as the package API name because the cloud worker
  is running wiki maintenance, not pretending to be a terminal user.
- Keep the API small:
  - operation: `init` or `ingest`
  - cwd
  - inputs for ingest
  - harness
  - optional title/guidance/root/name/description/force
  - result run id, run status, harness status, summary, output text
- Hosted backend tests should not require `codealmanac` to be installed in the
  backend venv. The Modal adapter must import `codealmanac.maintenance` lazily
  inside the function that only runs in the Modal image.
- Delete the hosted `almanac.services.updates.codealmanac` command builder once
  `updates_worker.py` stops using it. Compatibility command construction should
  not remain as dead architecture.
- Keep `modal_app/commands.py` for `modal_app/dev.py` diagnostics only. The
  production update worker should not import it.

## Task 1: Add CodeAlmanac Maintenance API

Files:

- Add `src/codealmanac/maintenance/__init__.py`
- Add `src/codealmanac/maintenance/requests.py`
- Add `src/codealmanac/maintenance/models.py`
- Add `src/codealmanac/maintenance/service.py`
- Add `tests/test_maintenance_api.py`
- Modify `tests/test_architecture.py`

Steps:

1. Add `MaintenanceOperation` with `INIT` and `INGEST`.
2. Add `RunMaintenanceRequest` with operation-specific validation:
   - `ingest` requires at least one input and rejects init-only fields.
   - `init` rejects inputs and accepts root/name/description/force.
3. Add `MaintenanceRunResult` with operation, run id, run status, harness
   status, summary, and output text.
4. Implement `run_maintenance(request, app=None)`:
   - create a default app when `app` is `None`
   - route `ingest` to `app.workflows.ingest.run(RunIngestRequest(...))`
   - route `init` to `app.workflows.init.run(RunInitRequest(...))`
5. Test ingest with a fake harness that writes one wiki page.
6. Test init with a fake harness that writes one wiki page.
7. Add an architecture test that the maintenance API imports workflows and
   request models but does not import `codealmanac.cli` or integrations.

## Task 2: Switch Hosted Worker To Direct Maintenance API

Files:

- Add `backend/modal_app/codealmanac_engine.py`
- Modify `backend/modal_app/updates_worker.py`
- Delete `backend/src/almanac/services/updates/codealmanac.py`
- Modify `backend/tests/test_modal_worker_contract.py`
- Modify `backend/tests/test_architecture_contract.py` if needed

Steps:

1. Add a hosted Modal helper that maps hosted `PullRequestSource`,
   `ConversationBatchSource`, and `BranchSource` to `RunMaintenanceRequest`.
2. Lazy-import `codealmanac.maintenance` from inside the helper.
3. For pull requests, call ingest with `inputs=("github:pr:<n>",)`.
4. For conversation batches, require a materialized source folder and call
   ingest with that folder as the only input.
5. For branch sources, call init against the checkout workspace.
6. Update `run_update` to call `run_codealmanac_engine(...)` and to post an
   error bundle if the direct call raises.
7. Remove command-builder tests and replace them with tests for direct request
   construction and worker AST checks.
8. Assert the production update worker does not import `run_command` or
   `codealmanac_command`.

## Task 3: Pin Hosted Runtime To The New CodeAlmanac Commit

Files:

- Modify `backend/modal_app/runtime.py`
- Modify `backend/tests/test_modal_worker_contract.py` if the expected pin
  contract changes

Steps:

1. Commit and push CodeAlmanac after Task 1 verification.
2. Update `CODEALMANAC_GIT_REF` to that commit SHA.
3. Keep Modal installing CodeAlmanac from git until deployment packaging is
   designed separately.

## Task 4: Update Launch Steering Docs

Files:

- Modify `docs/codealmanac-launch/worklog.md`
- Modify `docs/codealmanac-launch/progress.md`
- Modify `docs/codealmanac-launch/verification-matrix.md`
- Modify `docs/codealmanac-launch/next-agent-brief.md`

Steps:

1. Record that `codealmanac.maintenance` is the package API used by hosted
   workers.
2. Record that the hosted update worker no longer constructs public CLI
   commands.
3. Record the remaining risk: hosted delivery still needs expected-head
   commit/PR delivery and cloud SQL run-event storage maturity.
4. Move percentages forward conservatively after verification.

## Verification

CodeAlmanac focused gate:

```bash
cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest tests/test_maintenance_api.py tests/test_public_contract.py tests/test_architecture.py -q
uv run ruff check .
git diff --check
```

Hosted focused gate:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_modal_worker_contract.py tests/test_architecture_contract.py -q
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Full gates after focused checks pass:

```bash
cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest -q

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest -q
```
