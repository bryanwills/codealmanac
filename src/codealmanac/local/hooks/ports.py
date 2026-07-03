from pathlib import Path
from typing import Protocol

from codealmanac.local.hooks.models import (
    LocalGitHookChange,
    LocalGitHookName,
)


class LocalGitHookManager(Protocol):
    def install(self, repo_root: Path, hook: LocalGitHookName) -> LocalGitHookChange:
        """Install or repair one local Git hook."""

    def uninstall(self, repo_root: Path, hook: LocalGitHookName) -> LocalGitHookChange:
        """Remove one CodeAlmanac-managed local Git hook block."""
