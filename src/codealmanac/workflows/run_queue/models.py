from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.runs.models import RunRecord, RunWorkerSpawnResult


class RunQueueStartResult(CodeAlmanacModel):
    run: RunRecord
    worker: RunWorkerSpawnResult
