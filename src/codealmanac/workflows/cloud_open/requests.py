from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.cloud_auth.models import (
    DEFAULT_CLOUD_APP_URL,
    normalize_app_url,
)
from codealmanac.workflows.cloud_open.models import CloudOpenTarget


class OpenCloudTargetRequest(CodeAlmanacModel):
    cwd: Path
    target: CloudOpenTarget = "wiki"
    app_url: str = DEFAULT_CLOUD_APP_URL
    no_browser: bool = False

    @field_validator("app_url")
    @classmethod
    def normalize_app_url(cls, value: str) -> str:
        return normalize_app_url(value)
