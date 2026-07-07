from datetime import datetime

from codealmanac.services.runs.models import (
    PageChangeSet,
    RunRecord,
)
from codealmanac.services.runs.transcript import RunStep
from codealmanac.services.viewer.models import (
    ViewerJobPageChanges,
    ViewerJobRun,
    ViewerJobStep,
    ViewerJobTranscript,
)


def viewer_job_run(record: RunRecord) -> ViewerJobRun:
    return ViewerJobRun(
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
        page_changes=viewer_page_changes(record.page_changes),
        harness_transcript=viewer_harness_transcript(record),
    )


def viewer_job_step(step: RunStep) -> ViewerJobStep:
    return ViewerJobStep(
        sequence=step.sequence,
        timestamp=timestamp(step.timestamp),
        kind=step.kind.value,
        title=step.title,
        body=step.body,
        detail=step.detail,
        actor=step.actor,
        tool=step.tool,
        target=step.target,
        status=step.status,
        input=step.input,
        output=step.output,
        error=step.error,
    )


def viewer_page_changes(changes: PageChangeSet | None) -> ViewerJobPageChanges | None:
    if changes is None:
        return None
    return ViewerJobPageChanges(
        created=changes.created,
        updated=changes.updated,
        deleted=changes.deleted,
    )


def viewer_harness_transcript(record: RunRecord) -> ViewerJobTranscript | None:
    transcript = record.harness_transcript
    if transcript is None:
        return None
    return ViewerJobTranscript(
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
