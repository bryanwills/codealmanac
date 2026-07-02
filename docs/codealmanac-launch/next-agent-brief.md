# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, and push.

## Last Completed Slice

Slice 14 added local worker orchestration.

Implemented:

- `app.workflows.local_worker.run_next(...)`
- a typed local worker result containing preparation, engine, delivery, and
  final run records
- one-call success path: prepare one pending trigger, run the local engine, then
  deliver if the run is still `running`
- no-op path for no pending trigger
- failure paths for preparation failure and engine failure
- stale path where delivery is skipped if a newer trigger stales the run during
  engine execution

Verified:

```text
uv run pytest tests/test_local_worker_workflow.py tests/test_local_run_preparation_workflow.py tests/test_local_engine_workflow.py tests/test_local_delivery_workflow.py tests/test_architecture.py
uv run pytest
uv run ruff check .
git diff --check
```

## Next Pressure Test

Choose the next substantial slice from the launch plan. Good candidates:

- local trigger event recording through Git hooks
- public or hidden setup command that calls `app.local_hooks`
- local run storage bridge from repo-local job files to the control DB
- a hidden or internal CLI worker command that calls `app.workflows.local_worker`
- prompt restoration / first-build `init` path from
  `docs/codealmanac-launch/init-first-build-prompt-restoration.md`

Before coding, write the next slice plan under `docs/plans/`, then implement
the full slice, update this brief, update `progress.md`, send a RelayForge
progress update, commit, and push.

## Known Repo State

The branch is `dev`. At the end of Slice 14 verification it was ready to
commit on top of `origin/dev`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
