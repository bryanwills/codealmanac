from datetime import datetime
from enum import StrEnum

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.control.models import ControlDeliveryMode


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class DeliveryRecord(CodeAlmanacModel):
    id: str
    run_id: str
    mode: ControlDeliveryMode
    status: DeliveryStatus
    target_ref: str | None = None
    expected_head_sha: str | None = None
    delivered_head_sha: str | None = None
    commit_sha: str | None = None
    pr_url: str | None = None
    summary: str | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    finished_at: datetime | None = None

    @field_validator("id")
    @classmethod
    def require_id(cls, value: str) -> str:
        return required_text(value, "delivery id")

    @field_validator("run_id")
    @classmethod
    def require_run_id(cls, value: str) -> str:
        return required_text(value, "delivery run id")
