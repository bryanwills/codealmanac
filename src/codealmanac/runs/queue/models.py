from codealmanac.core.models import CodeAlmanacModel
from codealmanac.runs.ledger.models import RunRecord, RunWorkerSpawnResult


class RunQueueStartResult(CodeAlmanacModel):
    run: RunRecord
    worker: RunWorkerSpawnResult
