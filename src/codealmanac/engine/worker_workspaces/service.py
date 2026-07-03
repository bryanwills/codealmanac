from codealmanac.core.errors import ConflictError
from codealmanac.engine.worker_workspaces.models import (
    PreparedWorkerWorkspace,
    WorkerWorkspacePaths,
)
from codealmanac.engine.worker_workspaces.ports import GitWorktreeManager
from codealmanac.engine.worker_workspaces.requests import (
    PrepareWorkerWorkspaceRequest,
    ReadWorkerWorkspaceRequest,
    RemoveWorkerWorkspaceRequest,
)
from codealmanac.engine.worker_workspaces.store import WorkerWorkspacesStore


class WorkerWorkspacesService:
    def __init__(
        self,
        store: WorkerWorkspacesStore,
        git_worktrees: GitWorktreeManager,
    ):
        self.store = store
        self.git_worktrees = git_worktrees

    def prepare(
        self,
        request: PrepareWorkerWorkspaceRequest,
    ) -> PreparedWorkerWorkspace:
        paths = self.store.paths(request.run_id)
        if self.store.exists(paths):
            raise ConflictError(f"worker workspace already exists: {request.run_id}")
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
        return PreparedWorkerWorkspace(paths=paths, checkout=checkout)

    def paths(self, request: ReadWorkerWorkspaceRequest) -> WorkerWorkspacePaths:
        return self.store.paths(request.run_id)

    def remove(self, request: RemoveWorkerWorkspaceRequest) -> None:
        paths = self.store.paths(request.run_id)
        self.git_worktrees.remove(request.repository_root_path, paths.repo_path)
        self.store.remove_tree(paths)
