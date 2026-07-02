from pydantic import Field, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.cloud_auth.models import (
    DEFAULT_CLOUD_API_URL,
    normalize_api_url,
)
from codealmanac.services.cloud_repositories.models import CloudDeliveryMode


class CloudRepositoryRequest(CodeAlmanacModel):
    api_url: str = DEFAULT_CLOUD_API_URL

    @field_validator("api_url")
    @classmethod
    def normalize_api_url(cls, value: str) -> str:
        return normalize_api_url(value)


class ResolveCloudRepositoryRequest(CloudRepositoryRequest):
    full_name: str = Field(min_length=1)

    @field_validator("full_name")
    @classmethod
    def require_full_name(cls, value: str) -> str:
        return required_text(value, "cloud repository full name")


class ListCloudRepositoryTriggersRequest(CloudRepositoryRequest):
    repo_id: int = Field(gt=0)


class UpsertCloudRepositoryTriggerRequest(CloudRepositoryRequest):
    repo_id: int = Field(gt=0)
    branch: str = Field(min_length=1)
    enabled: bool | None = None
    delivery_mode: CloudDeliveryMode | None = None

    @field_validator("branch")
    @classmethod
    def require_branch(cls, value: str) -> str:
        return required_text(value, "cloud trigger branch")
