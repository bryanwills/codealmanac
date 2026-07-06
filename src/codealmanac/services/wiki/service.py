from pathlib import Path

from codealmanac.manual import ManualLibrary
from codealmanac.services.wiki.templates import (
    starter_page,
    starter_readme,
    starter_topics_yaml,
)
from codealmanac.services.workspaces.service import WorkspacesService


class WikiService:
    def __init__(self, workspaces: WorkspacesService, manual: ManualLibrary):
        self.workspaces = workspaces
        self.manual = manual

    def initialize(self, workspace_id: str) -> None:
        workspace = self.workspaces.get(workspace_id)
        almanac_path = workspace.almanac_path
        almanac_path.mkdir(parents=True, exist_ok=True)
        write_if_missing(almanac_path / "README.md", starter_readme())
        write_if_missing(almanac_path / "topics.yaml", starter_topics_yaml())
        write_if_missing(almanac_path / "getting-started.md", starter_page())


def write_if_missing(path: Path, body: str) -> None:
    if path.exists():
        return
    path.write_text(body, encoding="utf-8")
