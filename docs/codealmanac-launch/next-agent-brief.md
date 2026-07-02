# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, push, and RelayForge update.

## Last Completed Slice

Slice 32 added SQL-backed hosted run events.

Implemented:

- hosted worktree at
  `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
- hosted branch `codex/workos-authkit-api-foundation`
- hosted `RunEventKind` and `RunEvent` models
- hosted `RunEventRow` SQLModel table and `run_events` Supabase migration
  table
- hosted `run_event_from_row` conversion helper
- `UpdatesStore.append_run_event(...)` and
  `UpdatesStore.list_run_events(...)`
- automatic lifecycle events from `create_run`, `mark_running`,
  `mark_delivered`, and `mark_failed`
- event payloads limited to normalized metadata such as `worker_call_id`,
  `commit_sha`, `files_changed`, `summary`, and `error`
- pushed hosted commit `12cfc08 feat: persist hosted run events`

Verified:

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_update_run_events_contract.py tests/test_updates_contract.py tests/test_architecture_contract.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence
python -m compileall backend/src backend/modal_app -q
git diff --check
```

Counts: hosted focused `93 passed`; hosted full `306 passed, 1 warning`.

## Next Pressure Test

Harden expected-head delivery and expose useful run-event visibility.

Pressure points:

- hosted delivery still needs the expected-head check and commit/PR delivery
  policy path
- dashboard/API still does not expose run-event logs
- old inline-message conversation routes should remain compatibility-only

## Known Repo State

The CodeAlmanac branch is `dev`. Slice 31 is pushed to `origin/dev` at
`f20e928d feat: expose maintenance package api`.

The hosted auth branch is
`/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
on `codex/workos-authkit-api-foundation`. Slice 27 is pushed to origin at
`c91e162 feat: add v1 CLI auth routes`; Slice 28 is pushed to origin at
`36211ba feat: add capture credential API`; Slice 29 is pushed to origin at
`5644a65 feat: add capture transcript upload`; Slice 30 is pushed to origin at
`191d8d8 feat: materialize capture source refs`; Slice 31 is pushed to origin
at `51c2cb2 feat: call codealmanac maintenance api`; Slice 32 is pushed to
origin at `12cfc08 feat: persist hosted run events`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
