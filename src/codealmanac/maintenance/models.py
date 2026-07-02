from codealmanac.core.models import CodeAlmanacModel
from codealmanac.maintenance.requests import MaintenanceOperation
from codealmanac.services.harnesses.models import HarnessRunStatus
from codealmanac.services.runs.models import RunId, RunStatus


class MaintenanceRunResult(CodeAlmanacModel):
    operation: MaintenanceOperation
    run_id: RunId
    run_status: RunStatus
    harness_status: HarnessRunStatus
    summary: str | None
    output_text: str
