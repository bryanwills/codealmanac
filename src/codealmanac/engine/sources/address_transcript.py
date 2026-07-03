from codealmanac.core.errors import ValidationFailed
from codealmanac.engine.sources.address_hints import TRANSCRIPT_PROMPT_HINT
from codealmanac.engine.sources.models import (
    SourceBrief,
    SourceKind,
    SourceProvenanceKind,
    SourceRef,
)


def resolve_transcript(raw: str) -> SourceBrief:
    transcript = raw.removeprefix("transcript:").strip()
    if not transcript:
        raise ValidationFailed("transcript source requires an identifier or path")
    ref = SourceRef(
        raw=raw,
        kind=SourceKind.TRANSCRIPT,
        identity=f"transcript:{transcript}",
        transcript=transcript,
    )
    return SourceBrief(
        ref=ref,
        title=f"Transcript {transcript}",
        provenance_kind=SourceProvenanceKind.TRANSCRIPT,
        prompt_hint=TRANSCRIPT_PROMPT_HINT,
    )
