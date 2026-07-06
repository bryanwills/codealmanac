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
        return self.initialize_ready(request).workspace

    def build(self, request: InitializeWorkspaceRequest) -> BuildResult:
        return self.initialize_ready(request)

    def initialize_ready(self, request: InitializeWorkspaceRequest) -> BuildResult:
        workspace = self._initialize_workspace(request)
        index = self.index.ensure_fresh(workspace.workspace_id)
        return BuildResult(workspace=workspace, index=index)

    def _initialize_workspace(self, request: InitializeWorkspaceRequest) -> Workspace:
        target = self.workspaces.initialization_target(
            request.path,
            request.almanac_root,
        )
        workspace = self.workspaces.register(
            RegisterWorkspaceRequest(
                root_path=target.repo_root,
                almanac_root=target.almanac_root,
                name=request.name,
                description=request.description,
            )
        )
        self.wiki.initialize(workspace.workspace_id)
        return workspace
