# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, and push.

## Last Completed Slice

Slice 8 added local worker workspace preparation.

Implemented:

- `AppConfig.worker_workspaces_path`, defaulting to
  `~/.codealmanac/workspaces`
- `app.worker_workspaces`
- `src/codealmanac/services/worker_workspaces/`
- typed worker workspace paths for `repo/`, `sources/`, and `run/`
- `GitWorktreeManager` port
- `GitDetachedWorktreeManager` integration using
  `git worktree add --detach`
- conflict behavior for duplicate run workspace paths

Verified:

```text
uv run pytest tests/test_worker_workspaces_service.py tests/test_architecture.py
uv run pytest
uv run ruff check .
git diff --check
```

## Next Pressure Test

Choose the next substantial slice from the launch plan. Good candidates:

- local trigger event recording through Git hooks
- public or hidden setup command that calls `app.local_hooks`
- local run storage bridge from repo-local job files to the control DB
- active-run cancellation/staling when branch head changes
- source bundle selection materialization for claimed runs
- local run preparation workflow combining `claim_next_trigger`,
  `worker_workspaces`, source bundle refs, and `engine_runs`
- delivery commit application from `EngineRunResult`

Before coding, write the next slice plan under `docs/plans/`, then implement
the full slice, update this brief, update `progress.md`, send a RelayForge
progress update, commit, and push.

## Known Repo State

The branch is `dev`. At the start of Slice 8 it was clean and even with
`origin/dev`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
