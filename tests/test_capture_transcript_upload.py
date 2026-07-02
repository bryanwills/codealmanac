import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from codealmanac.integrations.capture import CaptureTranscriptNormalizer
from codealmanac.services.cloud_auth.models import CloudIdentity, CloudLoginSession
from codealmanac.services.cloud_auth.service import CloudAuthService
from codealmanac.services.cloud_auth.store import CloudAuthStore
from codealmanac.services.cloud_capture.event_store import CaptureEventStore
from codealmanac.services.cloud_capture.models import (
    CaptureArtifact,
    CaptureArtifactUpload,
    CaptureCloudStatus,
    CaptureRepositoryState,
    CaptureState,
    CaptureTranscriptUpload,
    CaptureTurnUploadResult,
)
from codealmanac.services.cloud_capture.requests import CaptureHookRequest
from codealmanac.services.cloud_capture.service import CloudCaptureService
from codealmanac.services.cloud_capture.store import CaptureStateStore


def test_codex_capture_hook_uploads_artifact_and_turn_metadata(tmp_path: Path) -> None:
    transcript = tmp_path / "codex.jsonl"
    transcript.write_text(
        json.dumps(
            {
                "timestamp": "2026-07-02T12:00:00Z",
                "payload": {"id": "sess_meta", "cwd": str(tmp_path)},
            }
        )
        + "\n"
        + json.dumps({"timestamp": "2026-07-02T12:01:00Z", "type": "response"})
        + "\n",
        encoding="utf-8",
    )
    client = FakeCloudCaptureClient()
    service = capture_service(tmp_path, client=client)

    event = service.record_hook(
        CaptureHookRequest(
            provider="codex",
            payload={
                "session_id": "sess_hook",
                "transcript_path": str(transcript),
                "cwd": str(tmp_path),
                "hook_event_name": "Stop",
                "turn_id": "turn_hook",
            },
        )
    )

    assert event.upload_status == "uploaded"
    assert event.artifact_ref == "source-artifacts://capture/test.jsonl"
    assert event.repo_full_name == "acme/api"
    assert event.branch == "dev"
    assert client.artifacts[0].provider == "codex"
    assert client.artifacts[0].provider_session_id == "sess_hook"
    assert client.artifacts[0].body == transcript.read_bytes()
    assert len(client.turns) == 1
    turn = client.turns[0]
    assert turn.provider_session_id == "sess_hook"
    assert turn.provider_turn_id == "turn_hook"
    assert turn.repo_full_name == "acme/api"
    assert turn.branch == "dev"
    assert turn.routing_status == "routable"
    assert turn.artifact_ref == "source-artifacts://capture/test.jsonl"


def test_claude_capture_hook_uses_deterministic_turn_fallback(tmp_path: Path) -> None:
    transcript = tmp_path / "claude.jsonl"
    transcript.write_text(
        json.dumps(
            {
                "timestamp": "2026-07-02T12:00:00Z",
                "sessionId": "claude-session",
                "cwd": str(tmp_path),
            }
        )
        + "\n"
        + json.dumps({"timestamp": "2026-07-02T12:03:00Z", "type": "assistant"})
        + "\n",
        encoding="utf-8",
    )
    first_client = FakeCloudCaptureClient()
    first = capture_service(tmp_path / "one", client=first_client)
    second_client = FakeCloudCaptureClient()
    second = capture_service(tmp_path / "two", client=second_client)
    payload = {
        "transcript_path": str(transcript),
        "cwd": str(tmp_path),
        "hook_event_name": "Stop",
    }

    first_event = first.record_hook(
        CaptureHookRequest(provider="claude", payload=payload)
    )
    second_event = second.record_hook(
        CaptureHookRequest(provider="claude", payload=payload)
    )

    assert first_event.upload_status == "uploaded"
    assert second_event.upload_status == "uploaded"
    assert (
        first_client.turns[0].provider_turn_id
        == second_client.turns[0].provider_turn_id
    )
    assert second_client.turns[0].provider_turn_id.startswith("turn_")
    assert second_client.turns[0].provider_session_id == "claude-session"


def test_missing_transcript_path_records_skipped_event(tmp_path: Path) -> None:
    client = FakeCloudCaptureClient()
    service = capture_service(tmp_path, client=client)

    event = service.record_hook(
        CaptureHookRequest(
            provider="codex",
            payload={
                "session_id": "sess_1",
                "transcript_path": str(tmp_path / "missing.jsonl"),
                "cwd": str(tmp_path),
            },
        )
    )

    assert event.upload_status == "skipped"
    assert event.upload_error == "missing transcript evidence"
    assert client.artifacts == []
    assert client.turns == []


def capture_service(
    tmp_path: Path,
    *,
    client: "FakeCloudCaptureClient",
) -> CloudCaptureService:
    tmp_path.mkdir(parents=True, exist_ok=True)
    state_store = CaptureStateStore(tmp_path / "capture.json")
    state_store.save(
        CaptureState(
            api_url="https://api.example.test",
            token="cap_secret",
            created_at=datetime(2026, 7, 2, 12, 0, tzinfo=UTC),
            providers=("codex", "claude"),
        )
    )
    return CloudCaptureService(
        auth=CloudAuthService(
            CloudAuthStore(tmp_path / "auth.json"),
            FakeCloudAuthClient(),
        ),
        store=state_store,
        events=CaptureEventStore(tmp_path / "capture-events"),
        client=client,
        hooks=FakeHookManager(),
        parser=CaptureTranscriptNormalizer(),
        repository_probe=FakeRepositoryProbe(),
    )


class FakeCloudCaptureClient:
    def __init__(self) -> None:
        self.artifacts: list[CaptureArtifactUpload] = []
        self.turns: list[CaptureTranscriptUpload] = []

    def issue_capture_credential(self, *, api_url: str, cli_token: str, name: str):
        raise NotImplementedError

    def capture_status(self, *, api_url: str, cli_token: str) -> CaptureCloudStatus:
        raise NotImplementedError

    def revoke_capture_credential(
        self,
        *,
        api_url: str,
        cli_token: str,
        capture_token: str,
    ) -> bool:
        raise NotImplementedError

    def upload_capture_artifact(
        self,
        *,
        api_url: str,
        capture_token: str,
        artifact: CaptureArtifactUpload,
    ) -> CaptureArtifact:
        assert api_url == "https://api.example.test"
        assert capture_token == "cap_secret"
        self.artifacts.append(artifact)
        return CaptureArtifact(
            ref="source-artifacts://capture/test.jsonl",
            sha256="0" * 64,
            size_bytes=len(artifact.body),
            content_type=artifact.content_type,
        )

    def upload_capture_turn(
        self,
        *,
        api_url: str,
        capture_token: str,
        turn: CaptureTranscriptUpload,
    ) -> CaptureTurnUploadResult:
        assert api_url == "https://api.example.test"
        assert capture_token == "cap_secret"
        self.turns.append(turn)
        return CaptureTurnUploadResult(
            accepted=True,
            routed=True,
            routing_status=turn.routing_status,
            source_id=uuid4(),
            turn_id=uuid4(),
            message_count=0,
        )


class FakeRepositoryProbe:
    def read(self, cwd: Path) -> CaptureRepositoryState:
        return CaptureRepositoryState(
            cwd=str(cwd),
            repo_available=True,
            repo_full_name="acme/api",
            branch="dev",
            head_sha="abc123",
        )


class FakeHookManager:
    pass


class FakeCloudAuthClient:
    def start_login(self, *, api_url: str) -> CloudLoginSession:
        raise NotImplementedError

    def poll_login(self, *, api_url: str, session_id) -> CloudLoginSession:
        raise NotImplementedError

    def me(self, *, api_url: str, token: str) -> CloudIdentity:
        raise NotImplementedError

    def logout(self, *, api_url: str, token: str) -> CloudIdentity:
        raise NotImplementedError
