from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text

CloudRunStatus = Literal["queued", "running", "delivered", "failed", "stale"]
CloudRunEventKind = Literal["status", "message", "tool", "output", "error"]


class CloudRunSource(CodeAlmanacModel):
    kind: str = Field(min_length=1)
    label: str = Field(min_length=1)
    url: str | None = None

    @field_validator("kind", "label")
    @classmethod
    def require_text(cls, value: str) -> str:
        return required_text(value, "cloud run source text")

    @field_validator("url")
    @classmethod
    def require_optional_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "cloud run source url")


class CloudRun(CodeAlmanacModel):
    run_id: UUID
    repo_id: int = Field(gt=0)
    source: CloudRunSource
    status: CloudRunStatus
    summary: str | None = None
    files_changed: tuple[str, ...] = ()
    commit_sha: str | None = None
    created_at: datetime | None = None
    finished_at: datetime | None = None

    @field_validator("summary", "commit_sha")
    @classmethod
    def require_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "cloud run text")

    @field_validator("files_changed")
    @classmethod
    def require_file_paths(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for path in value:
            required_text(path, "cloud run changed file")
        return value


class CloudRunEvent(CodeAlmanacModel):
    run_id: UUID
    sequence: int = Field(gt=0)
    timestamp: datetime
    kind: CloudRunEventKind
    message: str = Field(min_length=1)
    payload: dict[str, object] | None = None

    @field_validator("message")
    @classmethod
    def require_message(cls, value: str) -> str:
        return required_text(value, "cloud run event message")


class CloudRunPage(CodeAlmanacModel):
    items: tuple[CloudRun, ...]
    next_cursor: str | None = None

    @field_validator("next_cursor")
    @classmethod
    def require_optional_cursor(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "cloud run cursor")
