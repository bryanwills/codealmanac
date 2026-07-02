from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.control.models import BranchRecord, RepositoryRecord
from codealmanac.workflows.local_setup.models import LocalRepositoryState


class LocalStatusResult(CodeAlmanacModel):
    checkout: LocalRepositoryState
    repository: RepositoryRecord | None = None
    branch: BranchRecord | None = None

    @property
    def repository_configured(self) -> bool:
        return self.repository is not None

    @property
    def branch_configured(self) -> bool:
        return self.branch is not None
