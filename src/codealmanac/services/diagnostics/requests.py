from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.repositories.models import RepositoryName


class DoctorRequest(CodeAlmanacModel):
    cwd: Path
    repository_name: RepositoryName | None = None
