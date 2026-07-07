from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.harnesses.models import HarnessRunResult
from codealmanac.services.index.models import IndexRefreshResult
from codealmanac.services.repositories.models import Repository
from codealmanac.services.runs.models import RunId, RunRecord


class OperationContext(CodeAlmanacModel):
    run_id: RunId
    repository: Repository


class OperationResult(CodeAlmanacModel):
    run: RunRecord
    harness: HarnessRunResult
    index: IndexRefreshResult
