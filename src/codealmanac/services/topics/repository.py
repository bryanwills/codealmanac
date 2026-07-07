from pathlib import Path

from codealmanac.services.repositories.models import Repository, RepositoryName
from codealmanac.services.repositories.service import RepositoriesService


def resolve_topic_repository(
    repositories: RepositoriesService,
    cwd: Path,
    repository_name: RepositoryName | None,
) -> Repository:
    return repositories.select_for_read(cwd, repository_name)
