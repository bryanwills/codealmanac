from codealmanac.services.wiki.service import WikiService
from codealmanac.services.workspaces.models import Workspace
from codealmanac.services.workspaces.requests import (
    InitializeWorkspaceRequest,
    RegisterWorkspaceRequest,
)
from codealmanac.services.workspaces.service import WorkspacesService


class BuildWorkflow:
    def __init__(self, workspaces: WorkspacesService, wiki: WikiService):
        self.workspaces = workspaces
        self.wiki = wiki

    def initialize(self, request: InitializeWorkspaceRequest) -> Workspace:
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
