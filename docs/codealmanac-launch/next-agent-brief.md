# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, and push.

## Last Completed Slice

Slice 12 added deterministic local commit delivery.

Implemented:

- `app.deliveries`
- `app.workflows.local_delivery.deliver(...)`
- native Git delivery adapter for expected-head reads, wiki-only patch
  collection, patch application, and commit creation
- moved-head handling: skip delivery and mark the run `stale`
- empty-diff handling: skip delivery and mark the run `succeeded`
- worker workspace path lookup by run id

Verified:

```text
uv run pytest tests/test_deliveries_service.py tests/test_local_delivery_workflow.py tests/test_git_local_delivery.py tests/test_worker_workspaces_service.py tests/test_architecture.py
uv run pytest
uv run ruff check .
git diff --check
```

## Next Pressure Test

Choose the next substantial slice from the launch plan. Good candidates:

- local trigger event recording through Git hooks
- public or hidden setup command that calls `app.local_hooks`
- local run storage bridge from repo-local job files to the control DB
- local model worker execution from prepared `EngineRunRequest`

Before coding, write the next slice plan under `docs/plans/`, then implement
the full slice, update this brief, update `progress.md`, send a RelayForge
progress update, commit, and push.

## Known Repo State

The branch is `dev`. At the start of Slice 12 it was clean and even with
`origin/dev`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
