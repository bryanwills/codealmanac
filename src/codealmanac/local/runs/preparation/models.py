from codealmanac.core.models import CodeAlmanacModel
from codealmanac.engine.runs.models import PreparedEngineRun
from codealmanac.engine.source_bundles.models import MaterializedSourceBundle
from codealmanac.engine.workspaces.models import PreparedEngineWorkspace
from codealmanac.local.control.models import (
    BranchRecord,
    ControlRunRecord,
    RepositoryRecord,
    TriggerEventRecord,
)


class LocalRunPreparationResult(CodeAlmanacModel):
    prepared: bool
    reason: str | None = None
    repository: RepositoryRecord | None = None
    branch: BranchRecord | None = None
    trigger: TriggerEventRecord | None = None
    run: ControlRunRecord | None = None
    engine_workspace: PreparedEngineWorkspace | None = None
    source_bundle: MaterializedSourceBundle | None = None
    engine_run: PreparedEngineRun | None = None
