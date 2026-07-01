import json
from pathlib import Path

from pydantic import JsonValue

from codealmanac.integrations.sources.runtime import source_runtime_section
from codealmanac.integrations.sources.transcripts.models import (
    TranscriptRuntimeEntry,
)


def render_transcript_runtime(
    path: Path,
    entries: tuple[TranscriptRuntimeEntry, ...],
    max_chars: int,
) -> tuple[str, bool]:
    body = "\n".join(render_entry(entry) for entry in entries)
    return bounded_tail_text(
        "\n\n".join(
            (
                source_runtime_section(
                    "metadata",
                    f"path: {path}\nreadable_entries: {len(entries)}",
                ),
                source_runtime_section("transcript", body),
            )
        ),
        max_chars,
    )


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
