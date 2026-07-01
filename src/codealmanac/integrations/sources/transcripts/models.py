from enum import StrEnum

from pydantic import Field, JsonValue, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text


class TranscriptRuntimeLineKind(StrEnum):
    META = "meta"
    MESSAGE = "message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    EVENT = "event"
    RAW = "raw"


class TranscriptRuntimeEntry(CodeAlmanacModel):
    line_number: int
    kind: TranscriptRuntimeLineKind
    label: str
    text: str

    @field_validator("line_number")
    @classmethod
    def positive_line_number(cls, value: int) -> int:
        if value < 1:
            raise ValueError("line number must be positive")
        return value

    @field_validator("label", "text")
    @classmethod
    def require_text(cls, value: str) -> str:
        return required_text(value, "transcript runtime entry")


class TranscriptJsonLine(CodeAlmanacModel):
    # External provider JSON stays at this typed edge; entry normalization
    # validates known sub-shapes before it reads provider-specific fields.
    type: str | None = None
    timestamp: str | None = None
    session_id: str | None = Field(default=None, alias="sessionId")
    cwd: str | None = None
    payload: JsonValue | None = None
    message: JsonValue | None = None


class TranscriptPayload(CodeAlmanacModel):
    id: str | None = None
    cwd: str | None = None
    thread_source: str | None = None
    message: str | None = None
    item: JsonValue | None = None


class TranscriptMessage(CodeAlmanacModel):
    role: str | None = None
    content: JsonValue | None = None


class TranscriptItem(CodeAlmanacModel):
    type: str | None = None
    role: str | None = None
    name: str | None = None
    call_id: str | None = None
    content: JsonValue | None = None
    arguments: JsonValue | None = None
    output: JsonValue | None = None
