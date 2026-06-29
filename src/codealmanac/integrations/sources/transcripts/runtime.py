import json
from collections.abc import Iterator
from enum import StrEnum
from pathlib import Path

import jsonlines
from pydantic import Field, JsonValue, ValidationError, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.paths import normalize_path
from codealmanac.core.text import required_text
from codealmanac.integrations.sources.runtime import source_runtime_section
from codealmanac.services.sources.models import (
    SourceKind,
    SourceRef,
    SourceRuntime,
    SourceRuntimeStatus,
)
from codealmanac.services.sources.requests import InspectSourceRuntimeRequest

DEFAULT_MAX_CHARS = 60_000


class TranscriptRuntimeLineKind(StrEnum):
    META = "meta"
    MESSAGE = "message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    EVENT = "event"
    RAW = "raw"


class TranscriptRuntimeEntry(CodeAlmanacModel):
    line_number: int
    kind: TranscriptRuntimeLineKind
    label: str
    text: str

    @field_validator("line_number")
    @classmethod
    def positive_line_number(cls, value: int) -> int:
        if value < 1:
            raise ValueError("line number must be positive")
        return value

    @field_validator("label", "text")
    @classmethod
    def require_text(cls, value: str) -> str:
        return required_text(value, "transcript runtime entry")


class TranscriptJsonLine(CodeAlmanacModel):
    # External provider JSON is intentionally kept as JsonValue at this first
    # boundary; helpers below validate known sub-shapes before reading fields.
    type: str | None = None
    timestamp: str | None = None
    session_id: str | None = Field(default=None, alias="sessionId")
    cwd: str | None = None
    payload: JsonValue | None = None
    message: JsonValue | None = None


class TranscriptPayload(CodeAlmanacModel):
    id: str | None = None
    cwd: str | None = None
    thread_source: str | None = None
    message: str | None = None
    item: JsonValue | None = None


class TranscriptMessage(CodeAlmanacModel):
    role: str | None = None
    content: JsonValue | None = None


class TranscriptItem(CodeAlmanacModel):
    type: str | None = None
    role: str | None = None
    name: str | None = None
    call_id: str | None = None
    content: JsonValue | None = None
    arguments: JsonValue | None = None
    output: JsonValue | None = None


class TranscriptSourceRuntimeAdapter:
    def __init__(self, max_chars: int = DEFAULT_MAX_CHARS):
        self.max_chars = max_chars

    def supports(self, ref: SourceRef) -> bool:
        return ref.kind == SourceKind.TRANSCRIPT

    def inspect(self, request: InspectSourceRuntimeRequest) -> SourceRuntime:
        if request.ref.kind != SourceKind.TRANSCRIPT:
            return SourceRuntime(
                ref=request.ref,
                status=SourceRuntimeStatus.SKIPPED,
                title=f"Unsupported transcript source {request.ref.identity}",
            )
        path = transcript_path(request.cwd, request.ref)
        if path is None:
            return unavailable_runtime(
                request.ref,
                "Transcript unavailable",
                "transcript source requires a path",
            )
        if not path.is_file():
            return unavailable_runtime(
                request.ref,
                "Transcript unavailable",
                f"transcript file not found: {path}",
            )
        entries = tuple(read_transcript_entries(path))
        if len(entries) == 0:
            return unavailable_runtime(
                request.ref,
                f"Transcript {path}",
                "no readable JSONL objects found",
            )
        body = "\n".join(render_entry(entry) for entry in entries)
        content, truncated = bounded_tail_text(
            "\n\n".join(
                (
                    source_runtime_section(
                        "metadata",
                        f"path: {path}\nreadable_entries: {len(entries)}",
                    ),
                    source_runtime_section("transcript", body),
                )
            ),
            self.max_chars,
        )
        return SourceRuntime(
            ref=request.ref,
            status=SourceRuntimeStatus.AVAILABLE,
            title=f"Transcript {path}",
            content=content,
            truncated=truncated,
        )


def transcript_path(cwd: Path, ref: SourceRef) -> Path | None:
    if ref.transcript is None or ref.transcript.strip() == "":
        return None
    path = Path(ref.transcript).expanduser()
    if not path.is_absolute():
        path = cwd / path
    return normalize_path(path)


def unavailable_runtime(ref: SourceRef, title: str, diagnostic: str) -> SourceRuntime:
    return SourceRuntime(
        ref=ref,
        status=SourceRuntimeStatus.UNAVAILABLE,
        title=title,
        diagnostics=(diagnostic,),
    )


def read_transcript_entries(path: Path) -> Iterator[TranscriptRuntimeEntry]:
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            parsed = read_jsonl_object(line)
            if parsed is None:
                continue
            yield transcript_entry(line_number, parsed)


def read_jsonl_object(line: str) -> dict[str, object] | None:
    reader = jsonlines.Reader([line])
    return next(reader.iter(type=dict, skip_empty=True, skip_invalid=True), None)


def transcript_entry(
    line_number: int,
    parsed: dict[str, object],
) -> TranscriptRuntimeEntry:
    try:
        line = TranscriptJsonLine.model_validate(parsed)
    except ValidationError:
        return runtime_entry(
            line_number,
            TranscriptRuntimeLineKind.RAW,
            "raw",
            compact_json(parsed),
        )
    payload = parse_payload(line.payload)
    if payload is not None:
        entry = entry_from_payload(line_number, line, payload)
        if entry is not None:
            return entry
    message = parse_message(line.message)
    if message is not None:
        role = message.role or line.type or "message"
        return runtime_entry(
            line_number,
            TranscriptRuntimeLineKind.MESSAGE,
            label_with_timestamp(role, line.timestamp),
            line_message_text(line, message),
        )
    if line.session_id is not None or line.cwd is not None:
        text = "\n".join(
            part
            for part in (
                f"session_id: {line.session_id}" if line.session_id else "",
                f"cwd: {line.cwd}" if line.cwd else "",
            )
            if part
        )
        return runtime_entry(
            line_number,
            TranscriptRuntimeLineKind.META,
            label_with_timestamp(line.type or "meta", line.timestamp),
            text,
        )
    return runtime_entry(
        line_number,
        TranscriptRuntimeLineKind.RAW,
        label_with_timestamp(line.type or "raw", line.timestamp),
        compact_json(parsed),
    )


def entry_from_payload(
    line_number: int,
    line: TranscriptJsonLine,
    payload: TranscriptPayload,
) -> TranscriptRuntimeEntry | None:
    if payload.id is not None or payload.cwd is not None:
        text = "\n".join(
            part
            for part in (
                f"id: {payload.id}" if payload.id else "",
                f"cwd: {payload.cwd}" if payload.cwd else "",
                f"thread_source: {payload.thread_source}"
                if payload.thread_source
                else "",
            )
            if part
        )
        return runtime_entry(
            line_number,
            TranscriptRuntimeLineKind.META,
            label_with_timestamp(line.type or "payload", line.timestamp),
            text,
        )
    if payload.message is not None:
        return runtime_entry(
            line_number,
            TranscriptRuntimeLineKind.EVENT,
            label_with_timestamp(line.type or "event", line.timestamp),
            payload.message,
        )
    item = parse_item(payload.item)
    if item is None:
        return None
    return entry_from_item(line_number, line, item)


def entry_from_item(
    line_number: int,
    line: TranscriptJsonLine,
    item: TranscriptItem,
) -> TranscriptRuntimeEntry:
    if item.type in {"function_call", "tool_call"} or item.name is not None:
        return runtime_entry(
            line_number,
            TranscriptRuntimeLineKind.TOOL_CALL,
            label_with_timestamp(f"tool_call {item.name or 'unknown'}", line.timestamp),
            render_json_text(item.arguments),
        )
    if item.type in {"function_call_output", "tool_result"} or item.output is not None:
        return runtime_entry(
            line_number,
            TranscriptRuntimeLineKind.TOOL_RESULT,
            label_with_timestamp("tool_result", line.timestamp),
            render_json_text(item.output or item.content),
        )
    role = item.role or item.type or "item"
    return runtime_entry(
        line_number,
        TranscriptRuntimeLineKind.MESSAGE,
        label_with_timestamp(role, line.timestamp),
        render_json_text(item.content),
    )


def parse_payload(value: JsonValue | None) -> TranscriptPayload | None:
    if not isinstance(value, dict):
        return None
    try:
        return TranscriptPayload.model_validate(value)
    except ValidationError:
        return None


def parse_message(value: JsonValue | None) -> TranscriptMessage | None:
    if not isinstance(value, dict):
        return None
    try:
        return TranscriptMessage.model_validate(value)
    except ValidationError:
        return None


def parse_item(value: JsonValue | None) -> TranscriptItem | None:
    if not isinstance(value, dict):
        return None
    try:
        return TranscriptItem.model_validate(value)
    except ValidationError:
        return None


def line_message_text(line: TranscriptJsonLine, message: TranscriptMessage) -> str:
    parts = [
        part
        for part in (
            f"session_id: {line.session_id}" if line.session_id else "",
            f"cwd: {line.cwd}" if line.cwd else "",
            render_json_text(message.content),
        )
        if part
    ]
    return "\n".join(parts)


def runtime_entry(
    line_number: int,
    kind: TranscriptRuntimeLineKind,
    label: str,
    text: str,
) -> TranscriptRuntimeEntry:
    rendered = text.strip()
    if rendered == "":
        rendered = "(empty)"
    return TranscriptRuntimeEntry(
        line_number=line_number,
        kind=kind,
        label=label,
        text=rendered,
    )


def label_with_timestamp(label: str, timestamp: str | None) -> str:
    if timestamp is None or timestamp.strip() == "":
        return label
    return f"{label} {timestamp}"


def render_entry(entry: TranscriptRuntimeEntry) -> str:
    return f"L{entry.line_number:04d} [{entry.kind.value}] {entry.label}: {entry.text}"


def render_json_text(value: JsonValue | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(
            part for part in (render_json_text(item) for item in value) if part
        )
    if isinstance(value, dict):
        text = value.get("text")
        if isinstance(text, str):
            return text
        content = value.get("content")
        if content is not None:
            return render_json_text(content)
        return compact_json(value)
    return compact_json(value)


def compact_json(value: JsonValue) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def bounded_tail_text(value: str, max_chars: int) -> tuple[str, bool]:
    if len(value) <= max_chars:
        return value, False
    marker = "[truncated earlier transcript lines]\n\n"
    tail = value[-max_chars:]
    first_newline = tail.find("\n")
    if first_newline != -1:
        tail = tail[first_newline + 1 :]
    return marker + tail, True
