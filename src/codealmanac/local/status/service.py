from pathlib import Path

from codealmanac.core.errors import ValidationFailed
from codealmanac.local.control.requests import (
    FindBranchByNameRequest,
    FindRepositoryByLocalRootRequest,
)
from codealmanac.local.control.service import ControlService
from codealmanac.local.setup.ports import LocalRepositoryProbe
from codealmanac.local.status.models import LocalStatusResult
from codealmanac.local.status.requests import ReadLocalStatusRequest


class LocalStatusWorkflow:
    def __init__(
        self,
        control: ControlService,
        repository_probe: LocalRepositoryProbe,
    ):
        self.control = control
        self.repository_probe = repository_probe

    def status(self, request: ReadLocalStatusRequest) -> LocalStatusResult:
        checkout = self.repository_probe.read(request.cwd)
        if not checkout.available:
            return LocalStatusResult(checkout=checkout)
        repository_root = require_path(checkout.repository_root, "repository root")
        repository = self.control.find_repository_by_local_root(
            FindRepositoryByLocalRootRequest(root_path=repository_root)
        )
        if repository is None:
            return LocalStatusResult(checkout=checkout)
        branch = None
        if checkout.branch_name is not None:
            branch = self.control.find_branch_by_name(
                FindBranchByNameRequest(
                    repository_id=repository.id,
                    name=checkout.branch_name,
                )
            )
        return LocalStatusResult(
            checkout=checkout,
            repository=repository,
            branch=branch,
        )


def require_path(value: Path | None, name: str) -> Path:
    if value is None:
        raise ValidationFailed(f"{name} is required")
    return value
