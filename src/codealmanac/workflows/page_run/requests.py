from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.harnesses.models import HarnessKind
from codealmanac.services.runs.models import RunEventKind
from codealmanac.workflows.page_run.models import PageRunContext


class PageRunBeginRequest(CodeAlmanacModel):
    cwd: Path
    run_id: str
    wiki: str | None = None

    @field_validator("run_id")
    @classmethod
    def require_run_id(cls, value: str) -> str:
        return required_text(value, "page run id")


class PageRunRecordEventRequest(CodeAlmanacModel):
    context: PageRunContext
    kind: RunEventKind
    message: str

    @field_validator("message")
    @classmethod
    def require_message(cls, value: str) -> str:
        return required_text(value, "page run event message")


class PageRunExecuteRequest(CodeAlmanacModel):
    context: PageRunContext
    harness: HarnessKind
    prompt: str
    title: str | None = None
    success_summary: str

    @field_validator("prompt", "success_summary")
    @classmethod
    def require_text(cls, value: str) -> str:
        return required_text(value, "page run request text")

    @field_validator("title")
    @classmethod
    def require_optional_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "page run title")
