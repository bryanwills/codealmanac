from codealmanac.engine.harnesses.models import HarnessRunResult
from codealmanac.engine.lifecycle import harness_events, harness_run_event_kind
from codealmanac.services.control.models import ControlRunEventKind
from codealmanac.services.control.requests import AppendControlRunEventRequest
from codealmanac.services.control.service import ControlService


def record_harness_events(
    control: ControlService,
    run_id: str,
    harness: HarnessRunResult,
) -> None:
    for event in harness_events(harness):
        control.append_run_event(
            AppendControlRunEventRequest(
                run_id=run_id,
                kind=harness_run_event_kind(event),
                message=event.message,
                event_json=event.model_dump_json(),
            )
        )


def append_status(
    control: ControlService,
    run_id: str,
    message: str,
    artifact_ref: str | None = None,
) -> None:
    control.append_run_event(
        AppendControlRunEventRequest(
            run_id=run_id,
            kind=ControlRunEventKind.STATUS,
            message=message,
            artifact_ref=artifact_ref,
        )
    )


def append_error(
    control: ControlService,
    run_id: str,
    message: str,
    artifact_ref: str | None = None,
) -> None:
    control.append_run_event(
        AppendControlRunEventRequest(
            run_id=run_id,
            kind=ControlRunEventKind.ERROR,
            message=message,
            artifact_ref=artifact_ref,
        )
    )
