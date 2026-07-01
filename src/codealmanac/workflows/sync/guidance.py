from codealmanac.services.sources.models import TranscriptCandidate
from codealmanac.workflows.sync.models import SyncWorkItem


def sync_ingest_title(candidate: TranscriptCandidate) -> str:
    return f"Sync {candidate.app.value} transcript {candidate.session_id}"


def sync_ingest_guidance(item: SyncWorkItem) -> str:
    return "\n".join(
        (
            "Scheduled sync cursor:",
            f"- App: {item.candidate.app.value}",
            f"- Session id: {item.candidate.session_id}",
            f"- Transcript: {item.candidate.transcript_path}",
            f"- Previously absorbed through line: {item.entry.last_absorbed_line}",
            f"- Previously absorbed through byte: {item.entry.last_absorbed_size}",
            f"- Focus on line {item.from_line} onward.",
            "- You may inspect earlier lines only for context.",
            "- Do not re-document decisions already absorbed unless newer lines "
            "amend, invalidate, or add important nuance to them.",
        )
    )

