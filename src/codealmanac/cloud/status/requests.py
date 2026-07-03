from pathlib import Path

from pydantic import field_validator

from codealmanac.cloud.auth.models import (
    DEFAULT_CLOUD_API_URL,
    normalize_api_url,
)
from codealmanac.core.models import CodeAlmanacModel


class ReadCloudStatusRequest(CodeAlmanacModel):
    cwd: Path
    api_url: str = DEFAULT_CLOUD_API_URL
    check_capture_cloud: bool = False

    @field_validator("api_url")
    @classmethod
    def normalize_api_url(cls, value: str) -> str:
        return normalize_api_url(value)
