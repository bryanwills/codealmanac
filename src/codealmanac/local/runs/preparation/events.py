from codealmanac.engine.source_bundles.models import MaterializedSourceBundle
from codealmanac.local.control.models import (
    ControlRunEventKind,
    ControlRunRecord,
    ControlRunStatus,
)
from codealmanac.local.control.requests import (
    AppendControlRunEventRequest,
    UpdateControlRunRequest,
)
from codealmanac.local.control.service import ControlService


def append_prepared_events(
    control: ControlService,
    run: ControlRunRecord,
    source_bundle: MaterializedSourceBundle,
    source_ref: str,
) -> None:
    control.append_run_event(
        AppendControlRunEventRequest(
            run_id=run.id,
            kind=ControlRunEventKind.STATUS,
            message=(
                "materialized local source bundle "
                f"with {source_bundle.session_count} sessions"
            ),
            artifact_ref=source_ref,
        )
    )
    control.append_run_event(
        AppendControlRunEventRequest(
            run_id=run.id,
            kind=ControlRunEventKind.STATUS,
            message="prepared local engine workspace",
            artifact_ref=run.request_ref,
        )
    )


def fail_claimed_run(
    control: ControlService,
    run_id: str,
    message: str,
) -> ControlRunRecord:
    run = control.update_run(
        UpdateControlRunRequest(
            run_id=run_id,
            status=ControlRunStatus.FAILED,
            error=message,
        )
    )
    control.append_run_event(
        AppendControlRunEventRequest(
            run_id=run.id,
            kind=ControlRunEventKind.ERROR,
            message=message,
        )
    )
    return run
