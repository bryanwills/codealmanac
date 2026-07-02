# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, and push.

## Last Completed Slice

Slice 19 added public manual local update.

Implemented:

- `app.workflows.local_update.update(...)`
- public `codealmanac local update`
- manual trigger recording for the current configured checkout and branch
- same-head manual reruns after completed jobs
- duplicate active-job refusal when the branch already has a queued/running job
- manual pending-trigger replacement without changing normal hook duplicate
  behavior

Verified:

```text
uv run pytest tests/test_control_service.py tests/test_local_update_workflow.py tests/test_cli.py tests/test_architecture.py
uv run pytest
uv run ruff check .
git diff --check
```

## Next Pressure Test

Choose the next substantial slice from the launch plan. Good candidates:

- local trigger policy commands:
  `codealmanac local triggers list|enable|disable` and
  `codealmanac local delivery set`
- local run storage bridge from repo-local job files to the control DB, if
  needed for compatibility
- prompt restoration / first-build `init` path from
  `docs/codealmanac-launch/init-first-build-prompt-restoration.md`
- cloud public API/auth slice in `codealmanac-hosted`

Before coding, write the next slice plan under `docs/plans/`, then implement
the full slice, update this brief, update `progress.md`, send a RelayForge
progress update, commit, and push.

## Known Repo State

The branch is `dev`. At the end of Slice 19 verification it was ready to
commit on top of `origin/dev`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
