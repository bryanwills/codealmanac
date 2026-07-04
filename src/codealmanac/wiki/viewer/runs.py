from datetime import datetime

from codealmanac.runs.ledger.models import (
    PageChangeSet,
    RunLogEvent,
    RunRecord,
)
from codealmanac.wiki.viewer.models import (
    ViewerRunEvent,
    ViewerRunPageChanges,
    ViewerRunRecord,
    ViewerRunTranscript,
)


def viewer_run_record(record: RunRecord) -> ViewerRunRecord:
    return ViewerRunRecord(
        run_id=record.run_id,
        kind=record.kind.value,
        status=record.status.value,
        title=record.title,
        summary=record.summary,
        error=record.error,
        created_at=timestamp(record.created_at),
        updated_at=timestamp(record.updated_at),
        started_at=optional_timestamp(record.started_at),
        finished_at=optional_timestamp(record.finished_at),
        log_path=record.log_path,
        page_changes=viewer_page_changes(record.page_changes),
        harness_transcript=viewer_harness_transcript(record),
    )


def viewer_run_event(event: RunLogEvent) -> ViewerRunEvent:
    return ViewerRunEvent(
        sequence=event.sequence,
        timestamp=timestamp(event.timestamp),
        kind=event.kind.value,
        message=event.message,
        harness_event=event.harness_event,
    )


def viewer_page_changes(changes: PageChangeSet | None) -> ViewerRunPageChanges | None:
    if changes is None:
        return None
    return ViewerRunPageChanges(
        created=changes.created,
        updated=changes.updated,
        deleted=changes.deleted,
    )


def viewer_harness_transcript(record: RunRecord) -> ViewerRunTranscript | None:
    transcript = record.harness_transcript
    if transcript is None:
        return None
    return ViewerRunTranscript(
        kind=transcript.kind.value,
        session_id=transcript.session_id,
        transcript_path=transcript.transcript_path,
    )


def optional_timestamp(value: datetime | None) -> str | None:
    if value is None:
        return None
    return timestamp(value)


def timestamp(value: datetime) -> str:
    return value.isoformat()
