# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, and push.

## Last Completed Slice

Slice 17 added public local setup.

Implemented:

- `app.workflows.local_setup.setup(...)`
- `GitLocalRepositoryProbe`
- public `codealmanac local setup`
- branch policy registration in `~/.codealmanac/control.sqlite`
- local hook installation through setup
- `working-tree` local delivery support

Verified:

```text
uv run pytest tests/test_local_setup_workflow.py tests/test_cli.py tests/test_git_local_repository_probe.py tests/test_local_delivery_workflow.py tests/test_git_local_delivery.py tests/test_architecture.py
uv run pytest
uv run ruff check .
git diff --check
```

## Next Pressure Test

Choose the next substantial slice from the launch plan. Good candidates:

- public local status/update/jobs commands over the control DB
- local run storage bridge from repo-local job files to the control DB, if
  needed for compatibility
- prompt restoration / first-build `init` path from
  `docs/codealmanac-launch/init-first-build-prompt-restoration.md`
- cloud public API/auth slice in `codealmanac-hosted`

Before coding, write the next slice plan under `docs/plans/`, then implement
the full slice, update this brief, update `progress.md`, send a RelayForge
progress update, commit, and push.

## Known Repo State

The branch is `dev`. At the end of Slice 17 verification it was ready to
commit on top of `origin/dev`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
