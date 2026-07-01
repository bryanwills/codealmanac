from collections.abc import Iterator
from pathlib import Path

import jsonlines

from codealmanac.integrations.sources.transcripts.entries import transcript_entry
from codealmanac.integrations.sources.transcripts.models import (
    TranscriptRuntimeEntry,
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
