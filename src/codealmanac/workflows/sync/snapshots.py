from hashlib import sha256

from codealmanac.services.sources.models import TranscriptCandidate
from codealmanac.workflows.sync.models import TranscriptSnapshot

EMPTY_SHA256 = f"sha256:{sha256(b'').hexdigest()}"


def read_transcript(candidate: TranscriptCandidate) -> TranscriptSnapshot | None:
    try:
        content = candidate.transcript_path.read_bytes()
    except OSError:
        return None
    return TranscriptSnapshot(
        content=content,
        current_size=len(content),
        current_line=count_lines(content.decode("utf-8", errors="replace")),
    )


def sha256_bytes(content: bytes) -> str:
    return f"sha256:{sha256(content).hexdigest()}"


def count_lines(content: str) -> int:
    if content == "":
        return 0
    return content.count("\n") + (0 if content.endswith("\n") else 1)

