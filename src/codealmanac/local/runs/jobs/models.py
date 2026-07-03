from codealmanac.core.models import CodeAlmanacModel
from codealmanac.local.control.models import (
    BranchRecord,
    ControlRunEventRecord,
    ControlRunRecord,
    RepositoryRecord,
)


class LocalJobSummary(CodeAlmanacModel):
    run: ControlRunRecord
    repository: RepositoryRecord
    branch: BranchRecord


class LocalJobLogsResult(CodeAlmanacModel):
    job: LocalJobSummary
    events: tuple[ControlRunEventRecord, ...]
