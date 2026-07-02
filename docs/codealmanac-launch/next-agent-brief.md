# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, and push.

## Last Completed Slice

Slice 24 moved file-backed lifecycle job state out of repo-local Almanac roots
and into user-level CodeAlmanac state.

Implemented:

- `AppConfig.jobs_path`, defaulting to `~/.codealmanac/jobs`
- new run records, logs, queue specs, worker locks, and sync ledgers under
  `~/.codealmanac/jobs/<workspace-id>/`
- legacy read fallback for repo-local `<almanac-root>/jobs/`
- sync ledger load/write parity with the same user-level workspace jobs
  directory
- README, bundled manual, launch schema, and tests for the new storage contract
- retained `<almanac-root>/jobs/` in scaffold `.gitignore` blocks as a legacy
  compatibility guard

Verified:

```text
uv run pytest tests/test_runs_service.py tests/test_run_queue_workflow.py tests/test_sync_workflow.py tests/test_cli.py tests/test_public_contract.py tests/test_architecture.py -q
uv run pytest
uv run ruff check .
git diff --check
uv run codealmanac --help
uv run codealmanac dev ingest --help
uv run codealmanac dev garden --help
```

## Next Pressure Test

Choose the next substantial slice from the launch plan. Good candidates:

- cloud public API/auth slice in `codealmanac-hosted`
- hosted onboarding/repo configuration surface in `codealmanac-hosted`
- auto-update implementation for the CLI after researching a safe update
  library/mechanism

Before coding, write the next slice plan under `docs/plans/`, then implement
the full slice, update this brief, update `progress.md`, send a RelayForge
progress update, commit, and push.

## Known Repo State

The branch is `dev`. Slice 24 implementation commit `38423978` is pushed to
`origin/dev`. Start from the latest `origin/dev`, which includes the Slice 24
bookkeeping commit once this brief is committed and pushed.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
