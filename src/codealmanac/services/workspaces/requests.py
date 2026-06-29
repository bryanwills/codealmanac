from pathlib import Path

from pydantic import Field, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text


class RegisterWorkspaceRequest(CodeAlmanacModel):
    root_path: Path
    name: str | None = Field(
        default=None,
        description="None means derive the registry name from the root path.",
    )
    description: str = ""

    @field_validator("name")
    @classmethod
    def require_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "workspace name")


class InitializeWorkspaceRequest(CodeAlmanacModel):
    path: Path
    name: str | None = Field(
        default=None,
        description="None means derive the registry name from the workspace path.",
    )
    description: str = ""

    @field_validator("name")
    @classmethod
    def require_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "workspace name")


class SelectWorkspaceRequest(CodeAlmanacModel):
    selector: str
    base_path: Path | None = Field(
        default=None,
        description="None means relative path selectors are not resolved.",
    )

    @field_validator("selector")
    @classmethod
    def require_selector(cls, value: str) -> str:
        return required_text(value, "workspace selector")
