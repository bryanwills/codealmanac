from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.repositories.models import RepositoryName


class ShowPageRequest(CodeAlmanacModel):
    cwd: Path
    slug: str
    repository_name: RepositoryName | None = None

    @field_validator("slug")
    @classmethod
    def require_slug(cls, value: str) -> str:
        return required_text(value, "slug")
