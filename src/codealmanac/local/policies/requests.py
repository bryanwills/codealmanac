from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.local.control.models import ControlDeliveryMode


class ListLocalTriggerPoliciesRequest(CodeAlmanacModel):
    cwd: Path


class UpdateLocalTriggerPolicyRequest(CodeAlmanacModel):
    cwd: Path
    branch_name: str
    delivery_mode: ControlDeliveryMode | None = None

    @field_validator("branch_name")
    @classmethod
    def require_branch_name(cls, value: str) -> str:
        return required_text(value, "local trigger branch")


class SetLocalDeliveryPolicyRequest(CodeAlmanacModel):
    cwd: Path
    branch_name: str
    delivery_mode: ControlDeliveryMode

    @field_validator("branch_name")
    @classmethod
    def require_branch_name(cls, value: str) -> str:
        return required_text(value, "local delivery branch")
