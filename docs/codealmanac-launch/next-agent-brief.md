# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, push, and RelayForge update.

## Last Completed Slice

Slice 31 replaced the hosted worker subprocess bridge with a direct
CodeAlmanac maintenance package API call.

Implemented:

- hosted worktree at
  `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
- hosted branch `codex/workos-authkit-api-foundation`
- local CodeAlmanac `codealmanac.maintenance` package API over init and ingest
  workflows
- maintenance request/result models carrying operation, cwd, inputs, harness,
  run id, run status, harness status, summary, and output text
- hosted `backend/modal_app/codealmanac_engine.py` adapter from hosted
  `PullRequestSource`, `ConversationBatchSource`, and `BranchSource` to
  `codealmanac.maintenance`
- hosted production worker no longer imports `modal_app.commands`,
  `run_command`, or `codealmanac_command`
- deleted hosted `backend/src/almanac/services/updates/codealmanac.py`
- Modal image pin updated to CodeAlmanac commit
  `f20e928d5a62a1bb8b45ad670b90eac000011444`
- pushed hosted commit `51c2cb2 feat: call codealmanac maintenance api`

Verified:

```text
cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest tests/test_maintenance_api.py tests/test_public_contract.py tests/test_architecture.py -q
uv run pytest -q
uv run ruff check .
git diff --check

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_modal_worker_contract.py tests/test_architecture_contract.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence
python -m compileall backend/src backend/modal_app -q
git diff --check
```

Counts: local focused `91 passed`; local full `484 passed`; hosted focused
`81 passed`; hosted full `303 passed, 1 warning`.

## Next Pressure Test

Harden the remaining hosted run/delivery path now that the worker no longer
uses the public CLI bridge.

Pressure points:

- cloud run storage still needs SQL-backed `runs`, `run_events`, and durable
  run/source artifact refs that parallel the local control DB
- hosted delivery still needs the expected-head check and commit/PR delivery
  policy path
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
at `51c2cb2 feat: call codealmanac maintenance api`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
