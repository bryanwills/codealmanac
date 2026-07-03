from codealmanac.core.paths import normalize_path
from codealmanac.local.hooks.models import LocalGitHooksResult
from codealmanac.local.hooks.ports import LocalGitHookManager
from codealmanac.local.hooks.requests import (
    InstallLocalHooksRequest,
    UninstallLocalHooksRequest,
)


class LocalHooksService:
    def __init__(self, manager: LocalGitHookManager):
        self.manager = manager

    def install(self, request: InstallLocalHooksRequest) -> LocalGitHooksResult:
        repo_root = normalize_path(request.repo_root)
        return LocalGitHooksResult(
            repo_root=repo_root,
            changes=tuple(
                self.manager.install(repo_root, hook) for hook in request.hooks
            ),
        )

    def uninstall(self, request: UninstallLocalHooksRequest) -> LocalGitHooksResult:
        repo_root = normalize_path(request.repo_root)
        return LocalGitHooksResult(
            repo_root=repo_root,
            changes=tuple(
                self.manager.uninstall(repo_root, hook) for hook in request.hooks
            ),
        )
