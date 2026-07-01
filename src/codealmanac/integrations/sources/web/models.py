from enum import StrEnum

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text


class WebContentKind(StrEnum):
    HTML = "html"
    TEXT = "text"


class FetchedWebResponse(CodeAlmanacModel):
    final_url: str
    status_code: int
    content_type: str
    body: bytes
    response_truncated: bool = False

    @field_validator("final_url", "content_type")
    @classmethod
    def require_text_fields(cls, value: str) -> str:
        return required_text(value, "web response")

    @field_validator("status_code")
    @classmethod
    def validate_status_code(cls, value: int) -> int:
        if value < 100 or value > 599:
            raise ValueError("HTTP status code must be between 100 and 599")
        return value


class WebRuntimeDocument(CodeAlmanacModel):
    final_url: str
    status_code: int
    content_type: str
    content_kind: WebContentKind
    body: str
    title: str | None = None
    response_truncated: bool = False

    @field_validator("final_url", "content_type", "body")
    @classmethod
    def require_text_fields(cls, value: str) -> str:
        return required_text(value, "web runtime document")


class UnsupportedWebContentError(Exception):
    pass
