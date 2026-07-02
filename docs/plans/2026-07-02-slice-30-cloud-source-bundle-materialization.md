# Slice 30 Cloud Source Bundle Materialization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Teach codealmanac-hosted worker runs to materialize captured source-artifact refs into a worker-local `sources/` folder instead of passing rendered conversation content inline.

**Architecture:** SQL run records store source ids and artifact refs, never full transcript text. The backend owns source artifact storage and exposes a narrow internal read edge for workers. The Modal worker downloads refs into a deterministic `sources/` folder with a manifest, then invokes the current CodeAlmanac maintenance entrypoint against that folder as a bridge until the next worker-engine slice removes the remaining CLI process call.

**Tech Stack:** FastAPI internal routes, SQLModel stores, Pydantic update/source models, Modal worker Python helpers, httpx internal client, pytest, existing CodeAlmanac filesystem source runtime.

**Status:** Implemented on 2026-07-02.

---

## Decisions

- Preserve pass-by-reference semantics: `runs.source_json` may contain `batch_id`
  and artifact refs, but not copied transcript text or rendered conversation
  markdown.
- Use the existing internal API secret for worker artifact reads. This is a
  development-compatible bridge until the production source-artifact store is a
  shared Supabase bucket.
- Materialize the worker source folder as:

  ```text
  <worker>/sources/
    manifest.json
    sessions/<provider>/<provider-session-id>-<hash>.jsonl
  ```

- Capture-token turn uploads should schedule conversation ingest once the turn
  is routable, completed, and has a `source_ref`.
- The old inline-message upload routes remain accepted but should not drive the
  launch worker path unless they also have source refs.
- The Modal worker still invokes CodeAlmanac as a process in this slice, but it
  invokes the hidden maintenance surface with a source folder input:

  ```text
  codealmanac dev ingest <sources-dir> --foreground --using codex
  ```

  The next worker-engine slice should replace this with a direct Python engine
  call from the hosted worker.

## Task 1: Make Conversation Batch Runs Ref-Backed

Files:

- Modify `backend/src/almanac/services/updates/models.py`
- Modify `backend/src/almanac/services/updates/conversations.py`
- Modify `backend/src/almanac/services/conversations/models.py`
- Modify `backend/src/almanac/services/conversations/store.py`
- Modify `backend/tests/test_conversation_ingest_scheduler.py`
- Modify `backend/tests/test_modal_worker_contract.py`

Steps:

1. Add a small `ConversationBatchSourceRef` model with `provider`,
   `provider_session_id`, and `source_ref`.
2. Replace `ConversationBatchSource.source_text` with
   `source_refs: tuple[ConversationBatchSourceRef, ...]`.
3. Add a store query that returns distinct non-null source refs for the turns
   claimed by a batch.
4. Make due-batch selection require `conversation_sources.source_ref is not
   null`, so compatibility inline-message uploads do not enqueue unmaterializable
   worker runs.
5. Update capture-specific turn storage to call `ensure_ingest_state` when a
   completed routable turn has a source ref.
6. Update scheduler tests to prove run source JSON has refs and no inline text.

## Task 2: Add Internal Source Artifact Read

Files:

- Modify `backend/src/almanac/services/source_artifacts/models.py`
- Modify `backend/src/almanac/services/source_artifacts/ports.py`
- Modify `backend/src/almanac/services/source_artifacts/service.py`
- Modify `backend/src/almanac/services/source_artifacts/filesystem.py`
- Modify `backend/src/almanac/server/internal_router.py`
- Modify `backend/tests/test_internal_route_contract.py`
- Extend `backend/tests/test_capture_upload_api_contract.py` if needed

Steps:

1. Add a typed `SourceArtifactRead` result containing `ref`, `sha256`,
   `size_bytes`, `content_type`, and `body`.
2. Add `SourceArtifactStore.read(ref)` and `SourceArtifacts.read(ref)`.
3. In the filesystem store, accept only `source-artifacts://...` refs, normalize
   the key, reject traversal, and recompute sha256 while reading.
4. Add `GET /api/internal/source-artifacts?ref=...` protected by
   `internal_almanac`.
5. Return raw bytes with content type and sha headers; do not serialize the body
   into JSON.

## Task 3: Materialize Sources In The Modal Worker

Files:

- Add `backend/modal_app/source_artifacts.py`
- Modify `backend/modal_app/updates_worker.py`
- Modify `backend/modal_app/callback.py` only if a shared internal request helper
  is useful
- Modify `backend/src/almanac/services/updates/codealmanac.py`
- Modify `backend/tests/test_modal_worker_contract.py`

Steps:

1. Add an internal artifact client that downloads source refs from the backend
   with `X-Internal-Secret`.
2. Add a materializer that writes source files under `sources/sessions/...` and
   writes a `manifest.json` with all refs and local paths.
3. Make `run_update` materialize source refs before running CodeAlmanac for
   `ConversationBatchSource`.
4. Change the conversation-batch command to use:

   ```text
   codealmanac dev ingest <sources-dir> --foreground --using codex
   ```

5. Update PR and initial-branch commands to the current Python CLI shape where
   this slice touches them:

   ```text
   codealmanac dev ingest github:pr:<n> --foreground --using codex
   codealmanac init --using codex --yes
   ```

6. Keep command construction policy-free: it receives an already materialized
   path for conversation source runs.

## Task 4: Update Launch Steering Docs

Files:

- Modify `docs/codealmanac-launch/schema-contract.md`
- Modify `docs/codealmanac-launch/auth-api-contract.md`
- Modify `docs/codealmanac-launch/verification-matrix.md`
- Modify `docs/codealmanac-launch/worklog.md`
- Modify `docs/codealmanac-launch/progress.md`
- Modify `docs/codealmanac-launch/next-agent-brief.md`

Steps:

1. Record that cloud conversation batch runs are now ref-backed.
2. Record the internal artifact-read route and current filesystem-store
   limitation.
3. Record the remaining worker-engine gap: Modal still calls a process bridge
   and must later import/call the Python engine directly.
4. Move percentages forward conservatively after verification.

## Verification

Hosted backend focused gate:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_conversation_ingest_scheduler.py tests/test_capture_upload_api_contract.py tests/test_internal_route_contract.py tests/test_modal_worker_contract.py tests/test_architecture_contract.py -q
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Actual hosted verification:

```text
uv run pytest tests/test_conversation_ingest_scheduler.py tests/test_capture_upload_api_contract.py tests/test_internal_route_contract.py tests/test_modal_worker_contract.py tests/test_updates_contract.py tests/test_architecture_contract.py -q
# 119 passed, 1 warning

uv run pytest -q
# 301 passed, 1 warning

uv run ruff check .
uv run ruff format --check .
git diff --check
```

CodeAlmanac local docs/contract gate:

```bash
cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest tests/test_public_contract.py tests/test_architecture.py -q
uv run ruff check src tests
git diff --check
```

Full gates if focused checks pass and the touched surface is stable:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest -q

cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest -q
```
