from codealmanac.app import CodeAlmanac, create_app
from codealmanac.maintenance.models import MaintenanceRunResult
from codealmanac.maintenance.requests import (
    MaintenanceRunKind,
    RunMaintenanceRequest,
)
from codealmanac.workflows.ingest.requests import RunIngestRequest
from codealmanac.workflows.init.requests import RunInitRequest


def run_maintenance(
    request: RunMaintenanceRequest,
    app: CodeAlmanac | None = None,
) -> MaintenanceRunResult:
    resolved_app = create_app() if app is None else app
    if request.kind == MaintenanceRunKind.INIT:
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
            kind=request.kind,
            run_id=result.run.run_id,
            run_status=result.run.status,
            harness_status=result.harness.status,
            summary=result.run.summary,
            output_text=result.harness.output_text,
        )
    if request.kind == MaintenanceRunKind.INGEST:
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
            kind=request.kind,
            run_id=result.run.run_id,
            run_status=result.run.status,
            harness_status=result.harness.status,
            summary=result.run.summary,
            output_text=result.harness.output_text,
        )
    raise AssertionError(f"unsupported maintenance kind: {request.kind}")
