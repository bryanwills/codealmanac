from codealmanac.integrations.harnesses.codex.failures import classify_codex_failure
from codealmanac.integrations.harnesses.codex.state import CodexRunState
from codealmanac.services.harnesses.models import (
    HarnessEvent,
    HarnessEventKind,
    HarnessKind,
    HarnessRunResult,
    HarnessRunStatus,
)


def result_from_state(
    state: CodexRunState,
    events: list[HarnessEvent],
) -> HarnessRunResult:
    succeeded = state.success and state.failure is None
    output_text = state.result or state.error or "codex completed"
    return HarnessRunResult(
        kind=HarnessKind.CODEX,
        status=HarnessRunStatus.SUCCEEDED if succeeded else HarnessRunStatus.FAILED,
        output_text=output_text,
        summary=output_text.splitlines()[0],
        events=tuple(events),
    )


def failed_result(message: str) -> HarnessRunResult:
    failure = classify_codex_failure(message)
    event = HarnessEvent(
        kind=HarnessEventKind.ERROR,
        message=failure.message,
        failure=failure,
    )
    return HarnessRunResult(
        kind=HarnessKind.CODEX,
        status=HarnessRunStatus.FAILED,
        output_text=failure.message,
        summary=failure.message,
        events=(event,),
    )
