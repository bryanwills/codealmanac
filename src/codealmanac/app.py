from dataclasses import dataclass

from codealmanac.core.models import AppConfig
from codealmanac.services.wiki.service import WikiService
from codealmanac.services.workspaces.service import WorkspacesService
from codealmanac.services.workspaces.store import WorkspaceRegistryStore
from codealmanac.workflows.build.service import BuildWorkflow


@dataclass(frozen=True)
class CodeAlmanac:
    workspaces: WorkspacesService
    wiki: WikiService
    build: BuildWorkflow


def create_app(config: AppConfig | None = None) -> CodeAlmanac:
    app_config = config or AppConfig()
    workspaces = WorkspacesService(WorkspaceRegistryStore(app_config.registry_path))
    wiki = WikiService(workspaces)
    build = BuildWorkflow(workspaces, wiki)
    return CodeAlmanac(workspaces=workspaces, wiki=wiki, build=build)
