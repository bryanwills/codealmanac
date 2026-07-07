from pathlib import Path

from pydantic import Field

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.repositories.models import RepositoryName


class RegisterRepositoryRequest(CodeAlmanacModel):
    root_path: Path
    name: RepositoryName | None = Field(
        default=None,
        description="None means derive the database name from the root path.",
    )
    description: str = ""


class SelectRepositoryRequest(CodeAlmanacModel):
    name: RepositoryName
