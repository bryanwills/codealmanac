from typing import Literal

from pydantic import Field, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text

CloudDeliveryMode = Literal["commit", "pr"]


class CloudRepository(CodeAlmanacModel):
    repo_id: int = Field(gt=0)
    account_id: int = Field(gt=0)
    full_name: str = Field(min_length=1)
    default_branch: str = Field(min_length=1)

    @field_validator("full_name", "default_branch")
    @classmethod
    def require_text(cls, value: str) -> str:
        return required_text(value, "cloud repository text")


class CloudRepositoryPage(CodeAlmanacModel):
    items: tuple[CloudRepository, ...]
    next_cursor: str | None = None

    @field_validator("next_cursor")
    @classmethod
    def require_optional_cursor(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "cloud repository cursor")


class CloudRepositoryTriggerPolicy(CodeAlmanacModel):
    repo_id: int = Field(gt=0)
    branch: str = Field(min_length=1)
    enabled: bool
    delivery_mode: CloudDeliveryMode

    @field_validator("branch")
    @classmethod
    def require_branch(cls, value: str) -> str:
        return required_text(value, "cloud trigger branch")
