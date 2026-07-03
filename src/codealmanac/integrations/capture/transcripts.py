import hashlib
from datetime import UTC, datetime
from pathlib import Path

from codealmanac.cloud.capture.models import (
    CaptureArtifact,
    CaptureArtifactUpload,
    CaptureBranchSource,
    CaptureProvider,
    CaptureRepositoryState,
    CaptureRoutingStatus,
    CaptureTranscriptUpload,
)
from codealmanac.integrations.sources.transcripts.jsonl import (
    object_field,
    parse_json_object,
    string_field,
)


class CaptureTranscriptNormalizer:
    def normalize(
        self,
        *,
        provider: CaptureProvider,
        payload: dict[str, object],
        artifact: CaptureArtifact,
        repository: CaptureRepositoryState,
    ) -> CaptureTranscriptUpload | None:
        transcript_path_text = hook_string(payload, "transcript_path")
        if transcript_path_text is None:
            return None
        transcript_path = Path(transcript_path_text).expanduser()
        if not transcript_path.is_file():
            return None
        body = transcript_path.read_bytes()
        if len(body) == 0:
            return None
        metadata = transcript_metadata(provider, payload, body, transcript_path)
        return CaptureTranscriptUpload(
            provider=provider,
            provider_session_id=metadata.provider_session_id,
            provider_turn_id=metadata.provider_turn_id,
            transcript_path_hash=hash_text(str(transcript_path)),
            first_cwd=metadata.first_cwd,
            repo_full_name=(
                repository.repo_full_name if repository.repo_available else None
            ),
            branch=repository.branch,
            branch_source=branch_source(repository),
            routing_status=routing_status(repository),
            head_sha=repository.head_sha,
            started_at=metadata.started_at,
            completed_at=metadata.completed_at,
            artifact_ref=artifact.ref,
        )

    def artifact(
        self,
        *,
        provider: CaptureProvider,
        payload: dict[str, object],
    ) -> CaptureArtifactUpload | None:
        transcript_path_text = hook_string(payload, "transcript_path")
        if transcript_path_text is None:
            return None
        transcript_path = Path(transcript_path_text).expanduser()
        if not transcript_path.is_file():
            return None
        body = transcript_path.read_bytes()
        if len(body) == 0:
            return None
        provider_session_id = session_id(provider, payload, body)
        if provider_session_id is None:
            return None
        cwd = first_cwd(provider, payload, body)
        if cwd is None:
            return None
        return CaptureArtifactUpload(
            provider=provider,
            provider_session_id=provider_session_id,
            transcript_path=transcript_path,
            first_cwd=cwd,
            body=body,
        )


class CaptureTranscriptMetadata:
    def __init__(
        self,
        *,
        provider_session_id: str,
        provider_turn_id: str,
        first_cwd: str,
        started_at: datetime,
        completed_at: datetime | None,
    ) -> None:
        self.provider_session_id = provider_session_id
        self.provider_turn_id = provider_turn_id
        self.first_cwd = first_cwd
        self.started_at = started_at
        self.completed_at = completed_at


def transcript_metadata(
    provider: CaptureProvider,
    payload: dict[str, object],
    body: bytes,
    transcript_path: Path,
) -> CaptureTranscriptMetadata:
    parsed_lines = parsed_json_lines(body)
    provider_session_id = session_id(provider, payload, body) or "unknown-session"
    cwd = first_cwd(provider, payload, body) or "."
    provider_turn_id = hook_string(payload, "turn_id") or fallback_turn_id(
        transcript_path,
        parsed_lines,
    )
    timestamps = [
        timestamp
        for timestamp in (line_timestamp(line) for line in parsed_lines)
        if timestamp is not None
    ]
    started_at = timestamps[0] if timestamps else datetime.now(UTC)
    completed_at = timestamps[-1] if timestamps else None
    return CaptureTranscriptMetadata(
        provider_session_id=provider_session_id,
        provider_turn_id=provider_turn_id,
        first_cwd=cwd,
        started_at=started_at,
        completed_at=completed_at,
    )


def session_id(
    provider: CaptureProvider,
    payload: dict[str, object],
    body: bytes,
) -> str | None:
    hook_session_id = hook_string(payload, "session_id")
    if hook_session_id is not None:
        return hook_session_id
    for line in parsed_json_lines(body):
        if provider == "claude":
            found = string_field(line, "sessionId")
            if found is not None:
                return found
        else:
            codex_payload = object_field(line, "payload")
            if codex_payload is None:
                continue
            found = string_field(codex_payload, "id")
            if found is not None:
                return found
    return None


def first_cwd(
    provider: CaptureProvider,
    payload: dict[str, object],
    body: bytes,
) -> str | None:
    hook_cwd = hook_string(payload, "cwd")
    if hook_cwd is not None:
        return hook_cwd
    for line in parsed_json_lines(body):
        if provider == "claude":
            found = string_field(line, "cwd")
            if found is not None:
                return found
        else:
            codex_payload = object_field(line, "payload")
            if codex_payload is None:
                continue
            found = string_field(codex_payload, "cwd")
            if found is not None:
                return found
    return None


def parsed_json_lines(body: bytes) -> tuple[dict[str, object], ...]:
    lines: list[dict[str, object]] = []
    for line in body.decode("utf-8", errors="replace").splitlines():
        parsed = parse_json_object(line)
        if parsed is not None:
            lines.append(parsed)
    return tuple(lines)


def line_timestamp(line: dict[str, object]) -> datetime | None:
    value = string_field(line, "timestamp")
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def fallback_turn_id(
    transcript_path: Path,
    parsed_lines: tuple[dict[str, object], ...],
) -> str:
    last_line = repr(parsed_lines[-1]) if parsed_lines else ""
    return "turn_" + hash_text(f"{transcript_path}:{last_line}")[:24]


def routing_status(repository: CaptureRepositoryState) -> CaptureRoutingStatus:
    if not repository.repo_available:
        return "missing_repo"
    if repository.branch is None:
        return "missing_branch"
    return "routable"


def branch_source(repository: CaptureRepositoryState) -> CaptureBranchSource:
    if repository.repo_available and repository.branch is not None:
        return "git_fallback"
    return "missing"


def hook_string(payload: dict[str, object], key: str) -> str | None:
    value = payload.get(key)
    if isinstance(value, str) and value != "":
        return value
    return None


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
