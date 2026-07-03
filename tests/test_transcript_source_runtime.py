import json
from pathlib import Path

from codealmanac.app import create_app
from codealmanac.engine.sources.models import SourceRuntimeStatus
from codealmanac.engine.sources.requests import (
    InspectSourceRuntimeRequest,
    ResolveSourcesRequest,
)
from codealmanac.integrations.sources.transcripts import TranscriptSourceRuntimeAdapter


def test_transcript_runtime_reads_codex_jsonl(tmp_path: Path):
    transcript = tmp_path / "codex-session.jsonl"
    write_jsonl(
        transcript,
        (
            {
                "type": "session_meta",
                "payload": {"id": "codex-session", "cwd": str(tmp_path)},
            },
            {
                "type": "response_item",
                "payload": {
                    "item": {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "Keep the auth invariant in the wiki.",
                            }
                        ],
                    }
                },
            },
            {
                "type": "event_msg",
                "payload": {"message": "running source runtime test"},
            },
            {
                "type": "response_item",
                "payload": {
                    "item": {
                        "type": "function_call",
                        "name": "shell",
                        "arguments": {"cmd": "pytest"},
                    }
                },
            },
        ),
    )
    app = create_app(
        source_runtime_adapters=(TranscriptSourceRuntimeAdapter(),),
    )
    (brief,) = app.sources.resolve(
        ResolveSourcesRequest(cwd=tmp_path, inputs=(f"transcript:{transcript}",))
    )

    runtime = app.sources.inspect_runtime(
        InspectSourceRuntimeRequest(cwd=tmp_path, ref=brief.ref)
    )

    assert runtime.status == SourceRuntimeStatus.AVAILABLE
    assert "id: codex-session" in (runtime.content or "")
    assert "Keep the auth invariant in the wiki." in (runtime.content or "")
    assert "running source runtime test" in (runtime.content or "")
    assert '"cmd":"pytest"' in (runtime.content or "")


def test_transcript_runtime_reads_claude_jsonl(tmp_path: Path):
    transcript = tmp_path / "claude-session.jsonl"
    write_jsonl(
        transcript,
        (
            {
                "type": "user",
                "sessionId": "claude-session",
                "cwd": str(tmp_path),
                "message": {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Preserve the deploy gotcha."}
                    ],
                },
            },
            {
                "type": "assistant",
                "sessionId": "claude-session",
                "cwd": str(tmp_path),
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "Updated the wiki."}],
                },
            },
        ),
    )
    app = create_app(
        source_runtime_adapters=(TranscriptSourceRuntimeAdapter(),),
    )
    (brief,) = app.sources.resolve(
        ResolveSourcesRequest(cwd=tmp_path, inputs=(f"transcript:{transcript}",))
    )

    runtime = app.sources.inspect_runtime(
        InspectSourceRuntimeRequest(cwd=tmp_path, ref=brief.ref)
    )

    assert runtime.status == SourceRuntimeStatus.AVAILABLE
    assert "Preserve the deploy gotcha." in (runtime.content or "")
    assert "Updated the wiki." in (runtime.content or "")
    assert "session_id: claude-session" in (runtime.content or "")


def test_transcript_runtime_reports_missing_files(tmp_path: Path):
    app = create_app(source_runtime_adapters=(TranscriptSourceRuntimeAdapter(),))
    (brief,) = app.sources.resolve(
        ResolveSourcesRequest(cwd=tmp_path, inputs=("transcript:missing.jsonl",))
    )

    runtime = app.sources.inspect_runtime(
        InspectSourceRuntimeRequest(cwd=tmp_path, ref=brief.ref)
    )

    assert runtime.status == SourceRuntimeStatus.UNAVAILABLE
    assert runtime.content is None
    assert runtime.diagnostics == (
        f"transcript file not found: {tmp_path / 'missing.jsonl'}",
    )


def test_transcript_runtime_truncates_from_tail(tmp_path: Path):
    transcript = tmp_path / "large-session.jsonl"
    transcript.write_text(
        "\n".join(
            (
                '{"type":"event_msg","payload":{"message":"old transcript line"}}',
                '{"type":"event_msg","payload":{"message":"new transcript line"}}',
            )
        )
        + "\n",
        encoding="utf-8",
    )
    app = create_app(
        source_runtime_adapters=(TranscriptSourceRuntimeAdapter(max_chars=160),),
    )
    (brief,) = app.sources.resolve(
        ResolveSourcesRequest(cwd=tmp_path, inputs=(f"transcript:{transcript}",))
    )

    runtime = app.sources.inspect_runtime(
        InspectSourceRuntimeRequest(cwd=tmp_path, ref=brief.ref)
    )

    assert runtime.status == SourceRuntimeStatus.AVAILABLE
    assert runtime.truncated is True
    assert "[truncated earlier transcript lines]" in (runtime.content or "")
    assert "new transcript line" in (runtime.content or "")


def write_jsonl(path: Path, values: tuple[dict[str, object], ...]) -> None:
    path.write_text(
        "".join(f"{json.dumps(value)}\n" for value in values),
        encoding="utf-8",
    )
