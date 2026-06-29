from enum import StrEnum
from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text


class HarnessKind(StrEnum):
    CODEX = "codex"
    CLAUDE = "claude"


class HarnessRunStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HarnessReadiness(CodeAlmanacModel):
    kind: HarnessKind
    available: bool
    message: str

    @field_validator("message")
    @classmethod
    def require_message(cls, value: str) -> str:
        return required_text(value, "harness readiness message")


class HarnessTranscriptRef(CodeAlmanacModel):
    kind: HarnessKind
    session_id: str
    transcript_path: Path | None = None

    @field_validator("session_id")
    @classmethod
    def require_session_id(cls, value: str) -> str:
        return required_text(value, "harness transcript session id")


class HarnessRunResult(CodeAlmanacModel):
    kind: HarnessKind
    status: HarnessRunStatus
    output_text: str
    summary: str | None = None
    changed_files: tuple[Path, ...] = ()
    transcript: HarnessTranscriptRef | None = None

    @field_validator("output_text")
    @classmethod
    def require_output_text(cls, value: str) -> str:
        return required_text(value, "harness output")
