from pydantic import JsonValue, ValidationError

from codealmanac.integrations.sources.transcripts.models import (
    TranscriptItem,
    TranscriptJsonLine,
    TranscriptMessage,
    TranscriptPayload,
    TranscriptRuntimeEntry,
    TranscriptRuntimeLineKind,
)
from codealmanac.integrations.sources.transcripts.rendering import (
    compact_json,
    render_json_text,
)


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
