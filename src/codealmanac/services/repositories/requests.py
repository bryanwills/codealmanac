from pathlib import Path

from pydantic import Field, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.repositories.roots import (
    DEFAULT_ALMANAC_ROOT,
    validate_almanac_root_field,
)


class RegisterRepositoryRequest(CodeAlmanacModel):
    root_path: Path
    almanac_root: Path = Field(default=DEFAULT_ALMANAC_ROOT)
    name: str | None = Field(
        default=None,
        description="None means derive the database name from the root path.",
    )
    description: str = ""

    @field_validator("name")
    @classmethod
    def require_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "repository name")

    @field_validator("almanac_root")
    @classmethod
    def validate_almanac_root(cls, value: Path) -> Path:
        return validate_almanac_root_field(value)


class SelectRepositoryRequest(CodeAlmanacModel):
    name: str

    @field_validator("name")
    @classmethod
    def require_name(cls, value: str) -> str:
        return required_text(value, "repository name")
