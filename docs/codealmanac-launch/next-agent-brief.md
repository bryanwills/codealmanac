# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, push, and RelayForge update.

## Last Completed Slice

Slice 29 implemented capture transcript artifact upload through the narrow
`cap_...` credential.

Implemented:

- hosted worktree at
  `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
- hosted branch `codex/workos-authkit-api-foundation`
- hosted source-artifact service seam with filesystem-backed development store
- hosted `/v1/capture/artifacts` and `/v1/capture/turns`
- hosted `conversation_sources.source_ref` and matching migration
- hosted/frontend DTO mirrors for capture upload DTOs
- local Codex/Claude transcript normalizer for hook payloads
- local capture Git routing probe for repo/branch/head metadata
- local capture HTTP upload methods for raw artifact bytes and turn metadata
- hidden provider hook upload path with `upload_status` diagnostic events

Verified:

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_capture_tokens_api_contract.py tests/test_capture_upload_api_contract.py tests/test_hosted_conversation_sync_contract.py tests/test_conversation_ingest_scheduler.py tests/test_architecture_contract.py -q
uv run ruff check .

cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest tests/test_capture_transcript_upload.py tests/test_cloud_capture_service.py tests/test_cli.py tests/test_public_contract.py tests/test_architecture.py -q
uv run ruff check .
```

Counts: hosted focused backend `88 passed, 1 warning`; local focused tests
`147 passed`.

## Next Pressure Test

Slice 30 should materialize source-artifact refs into cloud worker source
bundles.

Pressure points:

- teach the cloud worker/source-bundle path to read `source_ref` artifacts
  instead of assuming inline `conversation_messages`
- preserve pass-by-reference semantics in prompts and worker request files
- decide whether capture-token turn uploads should mark ingest state due in the
  same slice that source refs become materializable
- keep the old `/api/cli/.../conversation-turns/*` inline-message route
  compatibility-only

## Known Repo State

The CodeAlmanac branch is `dev`. Slice 28 is pushed to `origin/dev` at
`40ff8e0c feat: add cloud capture setup`; Slice 29 is currently dirty and
ready for full verification, commit, and push.

The hosted auth branch is
`/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
on `codex/workos-authkit-api-foundation`. Slice 27 is pushed to origin at
`c91e162 feat: add v1 CLI auth routes`; Slice 28 is pushed to origin at
`36211ba feat: add capture credential API`. Slice 29 is currently dirty and
ready for full verification, commit, and push.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
