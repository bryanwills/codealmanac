from codealmanac.core.models import CodeAlmanacModel
from codealmanac.engine.harnesses.models import HarnessRunStatus
from codealmanac.maintenance.requests import MaintenanceRunKind
from codealmanac.runs.ledger.models import RunId, RunStatus


class MaintenanceRunResult(CodeAlmanacModel):
    kind: MaintenanceRunKind
    run_id: RunId
    run_status: RunStatus
    harness_status: HarnessRunStatus
    summary: str | None
    output_text: str
