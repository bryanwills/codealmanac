from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text

DEFAULT_CLOUD_API_URL = "https://codealmanac-backend-docker.onrender.com"

CloudLoginStatus = Literal["pending", "authorized", "complete", "expired"]
CloudLoginResultStatus = Literal[
    "signed_in",
    "already_signed_in",
    "expired",
    "timeout",
]


class CloudAuthState(CodeAlmanacModel):
    api_url: str = Field(min_length=1)
    token: str = Field(min_length=1)
    github_user_id: int
    github_login: str = Field(min_length=1)
    logged_in_at: datetime

    @field_validator("api_url")
    @classmethod
    def normalize_api_url(cls, value: str) -> str:
        return normalize_api_url(value)

    @field_validator("github_login")
    @classmethod
    def require_github_login(cls, value: str) -> str:
        return required_text(value, "GitHub login")


class CloudIdentity(CodeAlmanacModel):
    api_url: str
    github_user_id: int
    github_login: str

    @field_validator("api_url")
    @classmethod
    def normalize_api_url(cls, value: str) -> str:
        return normalize_api_url(value)


class CloudStatus(CodeAlmanacModel):
    api_url: str
    authenticated: bool
    github_user_id: int | None = None
    github_login: str | None = None

    @field_validator("api_url")
    @classmethod
    def normalize_api_url(cls, value: str) -> str:
        return normalize_api_url(value)


class CloudLoginSession(CodeAlmanacModel):
    session_id: UUID
    user_code: str
    verification_url: str
    expires_at: datetime
    status: CloudLoginStatus
    token: str | None = None


class CloudLoginResult(CodeAlmanacModel):
    api_url: str
    status: CloudLoginResultStatus
    github_user_id: int | None = None
    github_login: str | None = None
    verification_url: str | None = None
    user_code: str | None = None
    expires_at: datetime | None = None

    @field_validator("api_url")
    @classmethod
    def normalize_api_url(cls, value: str) -> str:
        return normalize_api_url(value)


class CloudLogoutResult(CodeAlmanacModel):
    api_url: str
    signed_out: bool
    github_user_id: int | None = None
    github_login: str | None = None

    @field_validator("api_url")
    @classmethod
    def normalize_api_url(cls, value: str) -> str:
        return normalize_api_url(value)


def normalize_api_url(value: str) -> str:
    text = required_text(value, "cloud API URL").rstrip("/")
    if not text.startswith(("https://", "http://")):
        raise ValueError("cloud API URL must start with http:// or https://")
    return text
