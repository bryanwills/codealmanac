from pathlib import Path
from typing import Protocol

from codealmanac.workflows.local_delivery.models import (
    LocalDeliveryCommit,
    LocalDeliveryHead,
    LocalDeliveryPatch,
)


class LocalGitDeliveryManager(Protocol):
    def read_head(self, repo_path: Path) -> LocalDeliveryHead:
        """Read the current branch and head SHA from the real checkout."""

    def collect_patch(
        self,
        worker_repo_path: Path,
        almanac_root: Path,
    ) -> LocalDeliveryPatch:
        """Collect a wiki-only patch from the detached worker repo."""

    def apply_patch_and_commit(
        self,
        repo_path: Path,
        almanac_root: Path,
        patch_text: str,
        commit_subject: str,
        commit_body: str | None,
    ) -> LocalDeliveryCommit:
        """Apply a validated patch and commit only the Almanac root."""
