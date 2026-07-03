from codealmanac.core.models import CodeAlmanacModel
from codealmanac.engine.source_bundles.models import MaterializedSourceBundle
from codealmanac.engine.worker_workspaces.models import PreparedWorkerWorkspace
from codealmanac.local.control.models import (
    BranchRecord,
    ControlRunRecord,
    RepositoryRecord,
    TriggerEventRecord,
)
from codealmanac.local.runs.artifacts.models import PreparedEngineRun


class LocalRunPreparationResult(CodeAlmanacModel):
    prepared: bool
    reason: str | None = None
    repository: RepositoryRecord | None = None
    branch: BranchRecord | None = None
    trigger: TriggerEventRecord | None = None
    run: ControlRunRecord | None = None
    worker_workspace: PreparedWorkerWorkspace | None = None
    source_bundle: MaterializedSourceBundle | None = None
    engine_run: PreparedEngineRun | None = None
