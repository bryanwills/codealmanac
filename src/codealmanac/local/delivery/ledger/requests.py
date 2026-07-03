from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.local.control.models import ControlDeliveryMode
from codealmanac.local.delivery.ledger.models import DeliveryStatus


class CreateDeliveryRequest(CodeAlmanacModel):
    run_id: str
    mode: ControlDeliveryMode
    target_ref: str | None = None
    expected_head_sha: str | None = None

    @field_validator("run_id")
    @classmethod
    def require_run_id(cls, value: str) -> str:
        return required_text(value, "delivery run id")

    @field_validator("target_ref", "expected_head_sha")
    @classmethod
    def require_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "delivery request text")


class ReadDeliveryRequest(CodeAlmanacModel):
    delivery_id: str

    @field_validator("delivery_id")
    @classmethod
    def require_delivery_id(cls, value: str) -> str:
        return required_text(value, "delivery id")


class UpdateDeliveryRequest(CodeAlmanacModel):
    delivery_id: str
    status: DeliveryStatus
    delivered_head_sha: str | None = None
    commit_sha: str | None = None
    pr_url: str | None = None
    summary: str | None = None
    error: str | None = None

    @field_validator("delivery_id")
    @classmethod
    def require_delivery_id(cls, value: str) -> str:
        return required_text(value, "delivery id")

    @field_validator(
        "delivered_head_sha",
        "commit_sha",
        "pr_url",
        "summary",
        "error",
    )
    @classmethod
    def require_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "delivery update text")
