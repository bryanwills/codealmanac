from codealmanac.app import CodeAlmanac, create_app
from codealmanac.maintenance.models import MaintenanceRunResult
from codealmanac.maintenance.requests import (
    MaintenanceOperation,
    RunMaintenanceRequest,
)
from codealmanac.workflows.ingest.requests import RunIngestRequest
from codealmanac.workflows.init.requests import RunInitRequest


def run_maintenance(
    request: RunMaintenanceRequest,
    app: CodeAlmanac | None = None,
) -> MaintenanceRunResult:
    resolved_app = create_app() if app is None else app
    if request.operation == MaintenanceOperation.INIT:
        result = resolved_app.workflows.init.run(
            RunInitRequest(
                path=request.cwd,
                harness=request.harness,
                almanac_root=request.almanac_root,
                name=request.name,
                description=request.description,
                title=request.title,
                guidance=request.guidance,
                force=request.force,
            )
        )
        return MaintenanceRunResult(
            operation=request.operation,
            run_id=result.run.run_id,
            run_status=result.run.status,
            harness_status=result.harness.status,
            summary=result.run.summary,
            output_text=result.harness.output_text,
        )
    if request.operation == MaintenanceOperation.INGEST:
        result = resolved_app.workflows.ingest.run(
            RunIngestRequest(
                cwd=request.cwd,
                inputs=request.inputs,
                harness=request.harness,
                title=request.title,
                guidance=request.guidance,
            )
        )
        return MaintenanceRunResult(
            operation=request.operation,
            run_id=result.run.run_id,
            run_status=result.run.status,
            harness_status=result.harness.status,
            summary=result.run.summary,
            output_text=result.harness.output_text,
        )
    raise AssertionError(f"unsupported maintenance operation: {request.operation}")
