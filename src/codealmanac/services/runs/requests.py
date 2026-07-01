from datetime import datetime, timedelta
from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.harnesses.models import HarnessEvent, HarnessTranscriptRef
from codealmanac.services.runs.models import (
    RunEventKind,
    RunId,
    RunOperation,
    RunSpec,
    RunStatus,
)


class ListRunsRequest(CodeAlmanacModel):
    cwd: Path
    wiki: str | None = None
    limit: int | None = None

    @field_validator("limit")
    @classmethod
    def non_negative_limit(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("limit must be non-negative")
        return value


class ShowRunRequest(CodeAlmanacModel):
    cwd: Path
    run_id: RunId
    wiki: str | None = None


class ReadRunLogRequest(CodeAlmanacModel):
    cwd: Path
    run_id: RunId
    wiki: str | None = None


class AttachRunRequest(CodeAlmanacModel):
    cwd: Path
    run_id: RunId
    wiki: str | None = None


class CancelRunRequest(CodeAlmanacModel):
    cwd: Path
    run_id: RunId
    wiki: str | None = None


class StartRunRequest(CodeAlmanacModel):
    cwd: Path
    operation: RunOperation
    wiki: str | None = None
    title: str | None = None


class QueueRunRequest(CodeAlmanacModel):
    cwd: Path
    spec: RunSpec
    wiki: str | None = None
    title: str | None = None


class ReadRunSpecRequest(CodeAlmanacModel):
    cwd: Path
    run_id: RunId
    wiki: str | None = None


class NextQueuedRunRequest(CodeAlmanacModel):
    cwd: Path
    wiki: str | None = None


class AcquireRunWorkerLockRequest(CodeAlmanacModel):
    cwd: Path
    wiki: str | None = None
    owner: str
    pid: int | None = None
    now: datetime | None = None
    stale_after: timedelta = timedelta(minutes=30)

    @field_validator("stale_after")
    @classmethod
    def positive_stale_after(cls, value: timedelta) -> timedelta:
        if value.total_seconds() <= 0:
            raise ValueError("worker lock stale_after must be positive")
        return value

    @field_validator("owner")
    @classmethod
    def require_owner(cls, value: str) -> str:
        return required_text(value, "run worker lock owner")

    @field_validator("pid")
    @classmethod
    def positive_pid(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("worker lock pid must be positive")
        return value


class SpawnRunWorkerRequest(CodeAlmanacModel):
    cwd: Path
    wiki: str | None = None


class RecordRunEventRequest(CodeAlmanacModel):
    cwd: Path
    run_id: RunId
    kind: RunEventKind
    message: str
    wiki: str | None = None
    harness_event: HarnessEvent | None = None


class MarkRunRunningRequest(CodeAlmanacModel):
    cwd: Path
    run_id: RunId
    wiki: str | None = None


class RecordRunHarnessTranscriptRequest(CodeAlmanacModel):
    cwd: Path
    run_id: RunId
    transcript: HarnessTranscriptRef
    wiki: str | None = None


class FinishRunRequest(CodeAlmanacModel):
    cwd: Path
    run_id: RunId
    status: RunStatus
    wiki: str | None = None
    summary: str | None = None
    error: str | None = None

    @field_validator("status")
    @classmethod
    def terminal_status(cls, value: RunStatus) -> RunStatus:
        if value not in {RunStatus.DONE, RunStatus.FAILED, RunStatus.CANCELLED}:
            raise ValueError("finish status must be done, failed, or cancelled")
        return value
