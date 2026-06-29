from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.harnesses.models import HarnessKind


class RunIngestRequest(CodeAlmanacModel):
    cwd: Path
    inputs: tuple[str, ...]
    harness: HarnessKind
    wiki: str | None = None
    title: str | None = None
    guidance: str | None = None

    @field_validator("inputs")
    @classmethod
    def require_inputs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) == 0:
            raise ValueError("at least one ingest input is required")
        return value

    @field_validator("title", "guidance")
    @classmethod
    def require_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "ingest request text")


class RunIngestWithRunRequest(RunIngestRequest):
    run_id: str

    @field_validator("run_id")
    @classmethod
    def require_run_id(cls, value: str) -> str:
        return required_text(value, "ingest run id")
