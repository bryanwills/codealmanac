# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, push, and RelayForge update.

## Last Completed Slice

Slice 33 added hosted stale delivery outcomes for expected-head drift.

Implemented:

- hosted worktree at
  `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
- hosted branch `codex/workos-authkit-api-foundation`
- `RunStatus.STALE` and `UpdateResult.stale(...)`
- typed `GitHubBranchHeadChanged` from GitHub commit expected-head drift
- product `StaleDelivery` in `services/updates/delivery.py`
- branch-head preflight checks for `CommitToBranch` and `OpenWikiPullRequest`
- `UpdatesStore.mark_stale(...)`, including a `run_events` status payload with
  expected and actual head SHAs
- completion handling that marks stale, skips billing, skips `RunDelivered`,
  and clears conversation-ingest active state
- backend/API/frontend DTO parity for the `stale` status
- frontend status metadata/icon rendering for stale runs
- pushed hosted commit `9098b65 feat: record stale delivery outcomes`

Verified:

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_updates_contract.py tests/test_update_run_events_contract.py tests/test_github_git_contract.py tests/test_repositories_api_contract.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
python -m compileall src modal_app -q

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence
git diff --check

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run lint
npm run test:frontend
npm run test:routes
```

Counts: hosted backend focused `38 passed, 1 warning`; hosted backend full
`311 passed, 1 warning`; hosted frontend `41 passed` and route tests
`26 passed`.

## Next Pressure Test

Expose useful run-event visibility and terminal failure/stale check surfaces.

Pressure points:

- dashboard/API still does not expose run-event logs
- terminal failed/stale runs still do not have a dedicated `RunFailed` or
  `RunStale` domain-event fanout for GitHub check updates
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
origin at `12cfc08 feat: persist hosted run events`; Slice 33 is pushed to
origin at `9098b65 feat: record stale delivery outcomes`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
