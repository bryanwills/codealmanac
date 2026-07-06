from pathlib import Path

from codealmanac.services.repositories.models import Repository
from codealmanac.services.repositories.service import RepositoriesService


def resolve_topic_repository(
    repositories: RepositoriesService,
    cwd: Path,
    wiki: str | None,
) -> Repository:
    return repositories.select_read_target(cwd, wiki)
