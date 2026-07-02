# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, push, and RelayForge update.

## Last Completed Slice

Slice 30 implemented hosted source-bundle materialization for captured
conversation refs.

Implemented:

- hosted worktree at
  `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
- hosted branch `codex/workos-authkit-api-foundation`
- hosted `ConversationBatchSource.source_refs` instead of inline
  `source_text`
- hosted conversation ingest scheduling only for completed, routable,
  ref-backed capture turns
- hosted source-artifact `read(ref)` service/store port
- protected internal route `GET /api/internal/source-artifacts?ref=...`
- Modal worker materialization into
  `.codealmanac-worker/sources/<batch-id>/manifest.json` and
  `sessions/<provider>/<provider-session-id>-<hash>.jsonl`
- hosted worker command bridge to the current Python CLI:
  `codealmanac dev ingest <sources-dir> --foreground --using codex`
- Modal image install of Python CodeAlmanac from a pinned git ref instead of
  the old npm package

Verified:

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_conversation_ingest_scheduler.py tests/test_capture_upload_api_contract.py tests/test_internal_route_contract.py tests/test_modal_worker_contract.py tests/test_updates_contract.py tests/test_architecture_contract.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence
git diff --check
```

Counts: focused hosted backend `119 passed, 1 warning`; full hosted backend
`301 passed, 1 warning`.

## Next Pressure Test

Remove or narrow the hosted worker subprocess bridge.

Pressure points:

- the hosted worker still calls `codealmanac` as a subprocess; the launch
  contract says workers should call the Python engine/model API directly
- the Modal image currently pins a CodeAlmanac git SHA, so the next slice must
  either update the pin intentionally or replace the package-level bridge
- cloud run storage still needs SQL-backed `runs`, `run_events`, and durable
  run/source artifact refs that parallel the local control DB
- hosted delivery still needs the expected-head check and commit/PR delivery
  policy path
- old inline-message conversation routes should remain compatibility-only

## Known Repo State

The CodeAlmanac branch is `dev`. Slice 29 is pushed to `origin/dev` at
`d7a33cba feat: upload captured transcripts`. Slice 30 only changes launch docs
in this repo.

The hosted auth branch is
`/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
on `codex/workos-authkit-api-foundation`. Slice 27 is pushed to origin at
`c91e162 feat: add v1 CLI auth routes`; Slice 28 is pushed to origin at
`36211ba feat: add capture credential API`; Slice 29 is pushed to origin at
`5644a65 feat: add capture transcript upload`; Slice 30 is pushed to origin at
`191d8d8 feat: materialize capture source refs`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
