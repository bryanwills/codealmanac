# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, and push.

## Last Completed Slice

Slice 4 added local Git hook installation and removal.

Implemented:

- `app.local_hooks.install(InstallLocalHooksRequest(...))`
- `app.local_hooks.uninstall(UninstallLocalHooksRequest(...))`
- Git adapter that resolves hook paths through
  `git rev-parse --git-path hooks/<hook>`
- managed hook blocks for `post-commit`, `post-merge`, and `post-rewrite`
- hook commands call `codealmanac __record-local-trigger`
- user hook content is preserved and reinstall is idempotent

Verified:

```text
uv run pytest tests/test_local_hooks.py tests/test_architecture.py
uv run ruff check .
git diff --check
```

## Next Pressure Test

Choose the next substantial slice from the launch plan. Good candidates:

- local trigger event recording through Git hooks
- public or hidden setup command that calls `app.local_hooks`
- local run storage bridge from repo-local job files to the control DB
- engine request/result models used by local and hosted workers

Before coding, write the next slice plan under `docs/plans/`, then implement
the full slice and update this brief.

## Known Repo State

The branch is `dev` and is behind `origin/dev` by one commit. Rebase or merge
before pushing if Git requires it.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
