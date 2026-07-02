from pathlib import Path

from pydantic import Field, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.cloud_auth.models import (
    DEFAULT_CLOUD_API_URL,
    normalize_api_url,
)
from codealmanac.services.cloud_repositories.models import CloudDeliveryMode


class CloudRepoRequest(CodeAlmanacModel):
    cwd: Path
    api_url: str = DEFAULT_CLOUD_API_URL

    @field_validator("api_url")
    @classmethod
    def normalize_api_url(cls, value: str) -> str:
        return normalize_api_url(value)


class ReadCloudRepoStatusRequest(CloudRepoRequest):
    pass


class ListCloudRepoTriggersRequest(CloudRepoRequest):
    pass


class UpdateCloudRepoTriggerRequest(CloudRepoRequest):
    branch: str = Field(min_length=1)
    delivery_mode: CloudDeliveryMode | None = None

    @field_validator("branch")
    @classmethod
    def require_branch(cls, value: str) -> str:
        return required_text(value, "cloud trigger branch")


class SetCloudRepoDeliveryRequest(CloudRepoRequest):
    branch: str = Field(min_length=1)
    delivery_mode: CloudDeliveryMode

    @field_validator("branch")
    @classmethod
    def require_branch(cls, value: str) -> str:
        return required_text(value, "cloud delivery branch")
