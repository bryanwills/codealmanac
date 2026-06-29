from codealmanac.services.index.service import IndexService
from codealmanac.services.wiki.service import WikiService
from codealmanac.services.workspaces.models import Workspace
from codealmanac.services.workspaces.requests import (
    InitializeWorkspaceRequest,
    RegisterWorkspaceRequest,
)
from codealmanac.services.workspaces.service import WorkspacesService
from codealmanac.workflows.build.models import BuildResult


class BuildWorkflow:
    def __init__(
        self,
        workspaces: WorkspacesService,
        wiki: WikiService,
        index: IndexService,
    ):
        self.workspaces = workspaces
        self.wiki = wiki
        self.index = index

    def initialize(self, request: InitializeWorkspaceRequest) -> Workspace:
        return self._initialize_workspace(request)

    def build(self, request: InitializeWorkspaceRequest) -> BuildResult:
        workspace = self._initialize_workspace(request)
        index = self.index.ensure_fresh(workspace.workspace_id)
        return BuildResult(workspace=workspace, index=index)

    def _initialize_workspace(self, request: InitializeWorkspaceRequest) -> Workspace:
        root_path = self.workspaces.initialization_root(request.path)
        workspace = self.workspaces.register(
            RegisterWorkspaceRequest(
                root_path=root_path,
                name=request.name,
                description=request.description,
            )
        )
        self.wiki.initialize(workspace.workspace_id)
        return workspace
