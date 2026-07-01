from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pydantic import field_validator, model_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.harnesses.models import HarnessKind, HarnessTranscriptRef


class RunOperation(StrEnum):
    BUILD = "build"
    INGEST = "ingest"
    SYNC = "sync"
    GARDEN = "garden"


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunEventKind(StrEnum):
    STATUS = "status"
    MESSAGE = "message"
    TOOL = "tool"
    OUTPUT = "output"
    ERROR = "error"


class PageChangeSet(CodeAlmanacModel):
    created: tuple[str, ...] = ()
    updated: tuple[str, ...] = ()
    archived: tuple[str, ...] = ()
    deleted: tuple[str, ...] = ()


class RunRecord(CodeAlmanacModel):
    run_id: str
    workspace_id: str
    operation: RunOperation
    status: RunStatus
    title: str | None
    summary: str | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    log_path: Path
    page_changes: PageChangeSet | None = None
    harness_transcript: HarnessTranscriptRef | None = None

    @field_validator("run_id")
    @classmethod
    def require_run_id(cls, value: str) -> str:
        return required_text(value, "run_id")

    @field_validator("workspace_id")
    @classmethod
    def require_workspace_id(cls, value: str) -> str:
        return required_text(value, "workspace_id")


class RunLogEvent(CodeAlmanacModel):
    run_id: str
    sequence: int
    timestamp: datetime
    kind: RunEventKind
    message: str

    @field_validator("run_id")
    @classmethod
    def require_run_id(cls, value: str) -> str:
        return required_text(value, "run_id")

    @field_validator("message")
    @classmethod
    def require_message(cls, value: str) -> str:
        return required_text(value, "message")

    @field_validator("sequence")
    @classmethod
    def positive_sequence(cls, value: int) -> int:
        if value < 1:
            raise ValueError("sequence must be positive")
        return value


TERMINAL_RUN_STATUSES = frozenset(
    (RunStatus.DONE, RunStatus.FAILED, RunStatus.CANCELLED)
)


class RunCancelResult(CodeAlmanacModel):
    record: RunRecord
    changed: bool


class RunAttachSnapshot(CodeAlmanacModel):
    record: RunRecord
    events: tuple[RunLogEvent, ...]
    terminal: bool


class RunSpec(CodeAlmanacModel):
    version: int = 1
    operation: RunOperation
    cwd: Path
    harness: HarnessKind
    wiki: str | None = None
    inputs: tuple[str, ...] = ()
    title: str | None = None
    guidance: str | None = None

    @field_validator("inputs")
    @classmethod
    def require_ingest_input_text(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for item in value:
            required_text(item, "run spec input")
        return value

    @field_validator("title", "guidance")
    @classmethod
    def require_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "run spec text")

    @model_validator(mode="after")
    def validate_operation_payload(self) -> "RunSpec":
        if self.version != 1:
            raise ValueError("run spec version must be 1")
        if self.operation == RunOperation.INGEST:
            if len(self.inputs) == 0:
                raise ValueError("ingest run spec requires inputs")
            return self
        if self.operation == RunOperation.GARDEN:
            if len(self.inputs) > 0:
                raise ValueError("garden run spec does not accept inputs")
            return self
        raise ValueError(f"unsupported queued run operation: {self.operation.value}")


class QueuedRun(CodeAlmanacModel):
    record: RunRecord
    spec: RunSpec | None


class RunWorkerLockOwner(CodeAlmanacModel):
    owner: str
    pid: int
    acquired_at: datetime

    @field_validator("owner")
    @classmethod
    def require_owner(cls, value: str) -> str:
        return required_text(value, "run worker lock owner")

    @field_validator("pid")
    @classmethod
    def positive_pid(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("worker lock pid must be positive")
        return value


class RunWorkerSpawnResult(CodeAlmanacModel):
    child_pid: int
    command: tuple[str, ...]

    @field_validator("child_pid")
    @classmethod
    def positive_child_pid(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("worker child pid must be positive")
        return value

    @field_validator("command")
    @classmethod
    def require_command(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) == 0:
            raise ValueError("worker command must not be empty")
        for part in value:
            required_text(part, "worker command part")
        return value


class RunQueueDrainResult(CodeAlmanacModel):
    lock_acquired: bool
    processed: tuple[RunRecord, ...] = ()
