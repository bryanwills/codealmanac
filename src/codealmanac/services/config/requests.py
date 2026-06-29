from pathlib import Path

from pydantic import Field, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text


class LoadConfigRequest(CodeAlmanacModel):
    cwd: Path
    wiki: str | None = Field(
        default=None,
        description="None means use the nearest project config.",
    )

    @field_validator("wiki")
    @classmethod
    def require_wiki(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "wiki selector")
