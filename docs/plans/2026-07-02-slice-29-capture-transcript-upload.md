# Slice 29 Capture Transcript Upload Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upload Codex/Claude transcript artifacts through the narrow `cap_...` capture credential and record normalized source metadata for cloud source selection.

**Architecture:** Capture upload is two-step and reference-based. The local hook uploads raw transcript bytes to a hosted source-artifact store with the capture token, then uploads normalized turn/session routing metadata that points at the stored artifact ref. SQL stores refs and metadata; it does not inline full transcript/session content for the capture-token path.

**Tech Stack:** FastAPI raw request bodies, SQLModel, Pydantic DTOs, file-backed artifact store seam for hosted tests/dev, argparse hidden hook, Git repository probing, existing provider transcript readers, pytest.

**Status:** Planned on 2026-07-02.

---

## Decisions

- Capture upload uses the `cap_...` token, not the `alm_...` CLI token.
- The local hook may send transcript bytes once to the hosted artifact endpoint.
  After that, every downstream system receives an artifact ref, not copied
  transcript content.
- Keep the existing `/api/cli/.../conversation-turns/*` routes for old hosted
  compatibility. Do not deepen them as the launch capture path.
- The hook remains fast and non-model-running. It uploads source evidence only.
- Provider raw JSON is parsed once at the local integration edge into typed
  normalized upload objects.
- Git branch/repo detection uses local Git state from the hook `cwd`; when it
  cannot resolve a GitHub repo or branch, upload the artifact and mark metadata
  as unroutable instead of guessing.

## Task 1: Hosted Source Artifact Store Seam

Files:

- Add `backend/src/almanac/services/source_artifacts/models.py`
- Add `backend/src/almanac/services/source_artifacts/ports.py`
- Add `backend/src/almanac/services/source_artifacts/service.py`
- Add `backend/src/almanac/services/source_artifacts/__init__.py`
- Add `backend/src/almanac/integrations/source_artifacts/filesystem.py`
- Modify `backend/src/almanac/app.py`
- Modify `backend/src/almanac/settings.py`
- Add `backend/tests/test_capture_upload_api_contract.py`

Contract:

```python
class SourceArtifactWrite(BaseModel):
    owner_id: str
    provider: Literal["codex", "claude"]
    provider_session_id: str
    content_sha256: str
    content_type: str
    body: bytes

class SourceArtifactRef(BaseModel):
    ref: str
    sha256: str
    size_bytes: int
    content_type: str
```

Implementation:

1. Add a service-owned `SourceArtifactStore` protocol with `write(...)`.
2. Add a filesystem adapter for tests/dev that writes under
   `settings.source_artifacts_path`.
3. Generate stable keys like:
   `capture/<owner-id>/<provider>/<provider-session-id>/<sha256>.jsonl`.
4. Return refs as `source-artifacts://capture/...`.
5. Do not add Supabase storage machinery in this slice. The seam makes a
   Supabase bucket adapter additive later.

Tests:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_capture_upload_api_contract.py -q
```

Expected first failure: missing `source_artifacts` service/imports.

## Task 2: Hosted Capture Upload API

Files:

- Modify `backend/src/almanac/server/capture_router.py`
- Add `backend/src/almanac/server/dtos/capture_uploads.py`
- Modify `backend/src/almanac/server/dtos/__init__.py`
- Modify `frontend/src/lib/api/dto/index.ts`
- Add `frontend/src/lib/api/dto/capture-uploads.ts`
- Modify `backend/tests/test_architecture_contract.py`
- Extend `backend/tests/test_capture_upload_api_contract.py`

Endpoints:

```text
POST /v1/capture/artifacts
POST /v1/capture/turns
```

Auth:

```text
Authorization: Bearer cap_...
```

Artifact upload:

```text
Headers:
  X-CodeAlmanac-Provider: codex|claude
  X-CodeAlmanac-Provider-Session-Id: <session-id>
Body:
  raw transcript bytes
Response:
  CaptureArtifactDTO { ref, sha256, sizeBytes, contentType }
```

Turn metadata upload:

```text
CaptureTurnUploadDTO:
  provider
  providerSessionId
  providerTurnId
  transcriptPathHash
  firstCwd
  repoFullName | null
  branch | null
  branchSource
  routingStatus
  headSha | null
  startedAt
  completedAt | null
  artifactRef
```

Implementation:

1. `POST /v1/capture/artifacts` uses `current_capture_user` and
   `almanac.source_artifacts.write(...)`.
2. `POST /v1/capture/turns` uses `current_capture_user`.
3. When `repoFullName` is present, resolve it through
   `almanac.conversations.resolve_repository(user, repoFullName)`.
4. Store a conversation source and turn through a new capture-specific
   conversation method that records `artifact_ref`/`source_ref` and no message
   content.
5. When `repoFullName` is missing or cannot be resolved, store artifact
   metadata as accepted but return a typed unroutable result. Do not guess a
   repo.

Tests:

- Capture token succeeds on both endpoints.
- CLI token is rejected by `/v1/capture/artifacts`.
- Artifact response never echoes transcript text.
- Turn upload stores `source_ref` and zero `conversation_messages`.
- Frontend DTO mirror tests include the new capture upload DTOs.

## Task 3: Hosted Conversation Source Ref Field

Files:

- Modify `backend/src/almanac/services/conversations/models.py`
- Modify `backend/src/almanac/services/conversations/tables.py`
- Modify `backend/src/almanac/services/conversations/records.py`
- Modify `backend/src/almanac/services/conversations/store.py`
- Modify `backend/src/almanac/services/conversations/service.py`
- Modify or add Supabase migration under `supabase/migrations/`
- Extend `backend/tests/test_hosted_conversation_sync_contract.py`
- Extend `backend/tests/test_conversation_ingest_scheduler.py` only if the
  existing scheduler assumes messages are always present.

Implementation:

1. Add nullable `source_ref` / `artifact_ref` to `conversation_sources`.
2. Keep `transcript_path_hash` for local privacy-preserving identity.
3. Add `Conversations.capture_turn(...)` that accepts repo resolution,
   normalized metadata, and `artifact_ref`.
4. Keep existing `start_turn` / `complete_turn` message-inline routes unchanged
   for compatibility.
5. Ensure source identity remains `(repo_id, provider, provider_session_id,
   transcript_path_hash)`.
6. Do not fetch artifact bytes during this slice's scheduler path. The next
   source-bundle slice should teach the cloud worker to read source refs.

Tests:

- Existing conversation sync tests still pass.
- New capture-specific tests prove `source_ref` is set.
- SQL migration includes the new nullable column and is safe for empty launch
  data.

## Task 4: Local Capture Transcript Normalization

Files:

- Add `src/codealmanac/integrations/capture/transcripts.py`
- Add `src/codealmanac/integrations/capture/repository.py`
- Modify `src/codealmanac/services/cloud_capture/models.py`
- Modify `src/codealmanac/services/cloud_capture/requests.py`
- Modify `src/codealmanac/services/cloud_capture/ports.py`
- Modify `src/codealmanac/services/cloud_capture/service.py`
- Modify `src/codealmanac/app.py`
- Add `tests/test_capture_transcript_upload.py`

Normalized local model:

```python
class CaptureTranscriptUpload(CodeAlmanacModel):
    provider: CaptureProvider
    provider_session_id: str
    provider_turn_id: str
    transcript_path: Path
    transcript_path_hash: str
    first_cwd: str
    repo_full_name: str | None
    branch: str | None
    branch_source: Literal["transcript", "git_fallback", "missing"]
    routing_status: Literal["routable", "missing_branch", "missing_repo"]
    head_sha: str | None
    started_at: datetime
    completed_at: datetime | None
```

Implementation:

1. Extract `transcript_path`, `cwd`, `session_id`, and `turn_id` from the hook
   payload.
2. Read the transcript file from `transcript_path`; reject paths that do not
   exist with a diagnostic event but keep hook exit code `0`.
3. Normalize Codex:
   - session id: hook payload `session_id`, otherwise Codex meta `payload.id`
   - cwd: hook payload `cwd`, otherwise Codex meta `payload.cwd`
   - turn id: hook payload `turn_id`, otherwise a stable hash from transcript
     path + last JSON line
4. Normalize Claude:
   - session id: hook payload `session_id`, otherwise first `sessionId`
   - cwd: hook payload `cwd`, otherwise first `cwd`
   - turn id: hook payload `turn_id`, otherwise stable hash from transcript
     path + last JSON line
5. Use a Git repository probe from the hook `cwd` to set repo full name, branch,
   and head SHA.
6. If repo is unavailable: `routing_status="missing_repo"`,
   `branch_source="missing"`.
7. If repo exists but branch is missing: `routing_status="missing_branch"`,
   `branch_source="missing"`.
8. If repo and branch exist: `routing_status="routable"`,
   `branch_source="git_fallback"`.

Tests:

- Codex fixture with hook `turn_id` uploads the exact provider turn id.
- Claude fixture without hook `turn_id` gets a deterministic fallback turn id.
- Missing transcript path records a diagnostic event and performs no upload.
- Missing repo uploads no turn metadata or uploads a typed unroutable result
  according to the final service contract; do not guess.

## Task 5: Local Capture Client Upload Methods

Files:

- Modify `src/codealmanac/integrations/cloud/http.py`
- Modify `src/codealmanac/services/cloud_capture/ports.py`
- Extend `tests/test_cloud_capture_service.py`
- Extend `tests/test_cli.py`

Client methods:

```python
upload_capture_artifact(api_url, capture_token, artifact) -> CaptureArtifact
upload_capture_turn(api_url, capture_token, turn) -> CaptureTurnUploadResult
```

Implementation:

1. Artifact upload uses `Authorization: Bearer <cap-token>`.
2. Artifact upload body is raw bytes, not JSON containing transcript text.
3. Turn upload uses JSON metadata containing `artifactRef`.
4. Hidden `__capture-hook` calls these methods after recording the local
   diagnostic event.
5. Hook upload failures are recorded locally and return exit code `0`; provider
   work must not be blocked by CodeAlmanac capture.

Tests:

- Fake cloud capture client sees the raw artifact bytes only in
  `upload_capture_artifact`.
- Fake cloud capture client sees no transcript body in `upload_capture_turn`.
- CLI hidden hook exits `0` after upload.
- CLI hidden hook exits `0` and records failure when upload raises.

## Task 6: Docs, Verification, Commit, Push, Relay

Files:

- Modify `docs/codealmanac-launch/auth-api-contract.md`
- Modify `docs/codealmanac-launch/schema-contract.md`
- Modify `docs/codealmanac-launch/cli-contract.md`
- Modify `docs/codealmanac-launch/verification-matrix.md`
- Modify `docs/codealmanac-launch/worklog.md`
- Modify `docs/codealmanac-launch/progress.md`
- Modify `docs/codealmanac-launch/next-agent-brief.md`

Verification commands:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_capture_tokens_api_contract.py tests/test_capture_upload_api_contract.py tests/test_hosted_conversation_sync_contract.py tests/test_conversation_ingest_scheduler.py tests/test_architecture_contract.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run test:routes
npm run test:frontend
npm run build

cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest tests/test_capture_transcript_upload.py tests/test_cloud_capture_service.py tests/test_cli.py tests/test_public_contract.py tests/test_architecture.py -q
uv run pytest -q
uv run ruff check .
git diff --check
```

Commit and push:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence
git add ...
git commit -m "feat: add capture transcript upload"
git push origin codex/workos-authkit-api-foundation

cd /Users/rohan/Desktop/Projects/codealmanac
git add ...
git commit -m "feat: upload captured transcripts"
git push origin dev
```

RelayForge update:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "Slice 29 shipped..."
```

## Out Of Scope

- Cloud worker source-bundle materialization from source artifact refs.
- Supabase Storage production adapter if the filesystem seam is enough to land
  tests and API contracts. Add it in the storage/deploy slice.
- Model execution from hooks.
- Browser onboarding UI for capture consent.
- Rate limiting.
