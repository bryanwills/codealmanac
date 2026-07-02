from pathlib import Path
from typing import Protocol

from codealmanac.services.worker_workspaces.models import GitWorktreeCheckout


class GitWorktreeManager(Protocol):
    def add_detached(
        self,
        source_repo_path: Path,
        worktree_path: Path,
        commit_sha: str,
    ) -> GitWorktreeCheckout:
        """Create a detached Git worktree for a specific commit."""

    def remove(
        self,
        source_repo_path: Path,
        worktree_path: Path,
    ) -> None:
        """Remove a Git worktree if it exists."""
