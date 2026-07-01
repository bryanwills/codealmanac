from codealmanac.services.sources.models import TranscriptCandidate


def transcript_sort_key(candidate: TranscriptCandidate) -> tuple[str, str, str]:
    return (
        candidate.app.value,
        str(candidate.transcript_path),
        candidate.session_id,
    )
