from codealmanac.core.models import CodeAlmanacModel
from codealmanac.local.control.models import BranchRecord, RepositoryRecord
from codealmanac.local.setup.models import LocalRepositoryState


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
