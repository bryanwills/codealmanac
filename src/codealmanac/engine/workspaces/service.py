from codealmanac.core.errors import ConflictError
from codealmanac.engine.workspaces.models import (
    EngineWorkspacePaths,
    PreparedEngineWorkspace,
)
from codealmanac.engine.workspaces.ports import GitWorktreeManager
from codealmanac.engine.workspaces.requests import (
    PrepareEngineWorkspaceRequest,
    ReadEngineWorkspaceRequest,
    RemoveEngineWorkspaceRequest,
)
from codealmanac.engine.workspaces.store import EngineWorkspacesStore


class EngineWorkspacesService:
    def __init__(
        self,
        store: EngineWorkspacesStore,
        git_worktrees: GitWorktreeManager,
    ):
        self.store = store
        self.git_worktrees = git_worktrees

    def prepare(
        self,
        request: PrepareEngineWorkspaceRequest,
    ) -> PreparedEngineWorkspace:
        paths = self.store.paths(request.run_id)
        if self.store.exists(paths):
            raise ConflictError(f"engine workspace already exists: {request.run_id}")
        self.store.create_non_repo_dirs(paths)
        try:
            checkout = self.git_worktrees.add_detached(
                request.repository_root_path,
                paths.repo_path,
                request.expected_head_sha,
            )
        except Exception:
            self.store.remove_tree(paths)
            raise
        return PreparedEngineWorkspace(paths=paths, checkout=checkout)

    def paths(self, request: ReadEngineWorkspaceRequest) -> EngineWorkspacePaths:
        return self.store.paths(request.run_id)

    def remove(self, request: RemoveEngineWorkspaceRequest) -> None:
        paths = self.store.paths(request.run_id)
        self.git_worktrees.remove(request.repository_root_path, paths.repo_path)
        self.store.remove_tree(paths)
