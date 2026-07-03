from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.local.control.models import (
    ControlRunRecord,
    TriggerEventRecord,
)
from codealmanac.local.runs.worker.models import LocalWorkerRunResult
from codealmanac.local.status.models import LocalStatusResult


class LocalUpdateResult(CodeAlmanacModel):
    started: bool
    reason: str | None = None
    status: LocalStatusResult
    trigger: TriggerEventRecord | None = None
    worker: LocalWorkerRunResult | None = None
    active_run: ControlRunRecord | None = None

    @field_validator("reason")
    @classmethod
    def require_optional_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "local update reason")
