from codealmanac.core.paths import normalize_path
from codealmanac.services.local_hooks.models import LocalGitHooksResult
from codealmanac.services.local_hooks.ports import LocalGitHookManager
from codealmanac.services.local_hooks.requests import (
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
