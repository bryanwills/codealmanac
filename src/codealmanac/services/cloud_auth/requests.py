from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.cloud_auth.models import (
    DEFAULT_CLOUD_API_URL,
    normalize_api_url,
)


class CloudAuthRequest(CodeAlmanacModel):
    api_url: str = DEFAULT_CLOUD_API_URL

    @field_validator("api_url")
    @classmethod
    def normalize_api_url(cls, value: str) -> str:
        return normalize_api_url(value)


class CloudLoginStartRequest(CloudAuthRequest):
    pass


class CloudLoginPollRequest(CloudAuthRequest):
    session_id: UUID


class SaveCloudTokenRequest(CloudAuthRequest):
    token: str = Field(min_length=1)
    logged_in_at: datetime


class CloudStatusRequest(CloudAuthRequest):
    validate_remote: bool = True


class CloudLogoutRequest(CloudAuthRequest):
    pass
