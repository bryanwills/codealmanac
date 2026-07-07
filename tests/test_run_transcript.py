from datetime import UTC, datetime

from codealmanac.services.harnesses.models import (
    HarnessEvent,
    HarnessEventKind,
    HarnessToolDisplay,
    HarnessToolDisplayKind,
    HarnessToolStatus,
)
from codealmanac.services.runs.models import RunEventKind, RunLogEvent
from codealmanac.services.runs.transcript import RunStepKind, project_run_steps


def test_project_run_steps_omits_empty_tool_detail() -> None:
    steps = project_run_steps(
        (
            RunLogEvent(
                run_id="run-1",
                sequence=1,
                timestamp=datetime(2026, 7, 7, 12, 0, tzinfo=UTC),
                kind=RunEventKind.TOOL,
                message="Agent spawnAgent",
                harness_event=HarnessEvent(
                    kind=HarnessEventKind.TOOL_USE,
                    message="Agent spawnAgent",
                    tool_id="tool-1",
                    tool_display=HarnessToolDisplay(
                        kind=HarnessToolDisplayKind.AGENT,
                        title="Agent spawnAgent",
                        status=HarnessToolStatus.STARTED,
                        provider_thread_id="thread-1",
                        provider_turn_id="turn-1",
                    ),
                ),
            ),
        )
    )

    assert len(steps) == 1
    assert steps[0].kind == RunStepKind.TOOL
    assert steps[0].title == "Agent spawnAgent"
    assert steps[0].detail is None
