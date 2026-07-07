from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import JsonValue, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.harnesses.models import (
    HarnessEvent,
    HarnessEventKind,
    HarnessToolDisplayKind,
)
from codealmanac.services.runs.models import RunEventKind, RunLogEvent


class RunStepKind(StrEnum):
    ASSISTANT = "assistant"
    TOOL = "tool"
    STATUS = "status"
    ERROR = "error"
    AGENT = "agent"


class RunStep(CodeAlmanacModel):
    sequence: int
    timestamp: datetime
    kind: RunStepKind
    title: str
    body: str | None = None
    detail: str | None = None
    actor: str | None = None
    tool: str | None = None
    target: str | None = None
    status: str | None = None
    input: str | None = None
    output: JsonValue | None = None
    error: bool = False

    @field_validator("title")
    @classmethod
    def require_title(cls, value: str) -> str:
        return required_text(value, "run step title")

    @field_validator("body", "detail", "actor", "tool", "target", "status", "input")
    @classmethod
    def require_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "run step text")


def project_run_steps(events: tuple[RunLogEvent, ...]) -> tuple[RunStep, ...]:
    projector = RunProjector()
    for event in events:
        projector.add(event)
    return tuple(projector.steps)


class RunProjector:
    def __init__(self) -> None:
        self.steps: list[RunStep] = []
        self.tools: dict[str, RunStep] = {}

    def add(self, event: RunLogEvent) -> None:
        harness_event = event.harness_event
        if harness_event is None:
            self.add_run_event(event)
            return
        self.add_harness_event(event, harness_event)

    def add_run_event(self, event: RunLogEvent) -> None:
        kind = (
            RunStepKind.ERROR
            if event.kind == RunEventKind.ERROR
            else RunStepKind.STATUS
        )
        title = (
            "Error" if event.kind == RunEventKind.ERROR else status_title(event.message)
        )
        self.steps.append(
            RunStep(
                sequence=event.sequence,
                timestamp=event.timestamp,
                kind=kind,
                title=title,
                body=event.message,
                error=event.kind == RunEventKind.ERROR,
            )
        )

    def add_harness_event(
        self,
        event: RunLogEvent,
        harness_event: HarnessEvent,
    ) -> None:
        match harness_event.kind:
            case HarnessEventKind.TEXT | HarnessEventKind.TEXT_DELTA:
                self.add_text(event, harness_event)
            case HarnessEventKind.TOOL_USE:
                self.add_tool(event, harness_event)
            case HarnessEventKind.TOOL_RESULT | HarnessEventKind.TOOL_SUMMARY:
                self.add_tool_result(event, harness_event)
            case (
                HarnessEventKind.AGENT_SPAWNED
                | HarnessEventKind.AGENT_WAIT_STARTED
                | HarnessEventKind.AGENT_COMPLETED
            ):
                self.add_agent(event, harness_event)
            case HarnessEventKind.ERROR:
                self.add_error(event, harness_event)
            case HarnessEventKind.WARNING:
                self.add_status(event, "Warning", harness_event.message)
            case HarnessEventKind.DONE:
                if harness_event.failure is not None:
                    self.add_error(event, harness_event)
                elif harness_event.message:
                    self.add_status(event, "Done", harness_event.message)
            case HarnessEventKind.PROVIDER_SESSION:
                if harness_event.provider_session_id:
                    self.add_status(
                        event,
                        "Session",
                        harness_event.provider_session_id,
                    )
            case HarnessEventKind.CONTEXT_USAGE:
                return

    def add_text(self, event: RunLogEvent, harness_event: HarnessEvent) -> None:
        actor = actor_label(harness_event)
        previous = self.steps[-1] if self.steps else None
        if (
            previous is not None
            and previous.kind == RunStepKind.ASSISTANT
            and previous.actor == actor
        ):
            self.steps[-1] = previous.model_copy(
                update={"body": join_text(previous.body, harness_event.message)}
            )
            return
        self.steps.append(
            RunStep(
                sequence=event.sequence,
                timestamp=event.timestamp,
                kind=RunStepKind.ASSISTANT,
                title=actor or "Assistant",
                body=harness_event.message,
                actor=actor,
            )
        )

    def add_tool(self, event: RunLogEvent, harness_event: HarnessEvent) -> None:
        step = RunStep(
            sequence=event.sequence,
            timestamp=event.timestamp,
            kind=RunStepKind.TOOL,
            title=tool_title(harness_event),
            body=tool_summary(harness_event),
            detail=tool_detail(harness_event),
            tool=tool_kind(harness_event),
            target=tool_target(harness_event),
            status=tool_status(harness_event) or "started",
            input=harness_event.tool_input,
            error=harness_event.tool_is_error is True,
        )
        self.steps.append(step)
        if harness_event.tool_id is not None:
            self.tools[harness_event.tool_id] = step

    def add_tool_result(self, event: RunLogEvent, harness_event: HarnessEvent) -> None:
        step = self.matching_tool(harness_event)
        if step is None:
            self.add_tool(event, harness_event)
            step = self.steps[-1]
        update: dict[str, Any] = {
            "sequence": event.sequence,
            "timestamp": event.timestamp,
            "status": tool_status(harness_event) or step.status or "completed",
            "output": harness_event.tool_result,
            "error": harness_event.tool_is_error is True,
        }
        summary = tool_summary(harness_event)
        if summary is not None:
            update["body"] = summary
        detail = tool_detail(harness_event)
        if detail is not None:
            update["detail"] = detail
        self.replace_step(step, step.model_copy(update=update))

    def add_agent(self, event: RunLogEvent, harness_event: HarnessEvent) -> None:
        trace = harness_event.agent_trace
        self.steps.append(
            RunStep(
                sequence=event.sequence,
                timestamp=event.timestamp,
                kind=RunStepKind.AGENT,
                title=agent_title(harness_event),
                body=trace.result if trace is not None else harness_event.message,
                detail=trace.prompt if trace is not None else None,
                status=agent_status(harness_event),
            )
        )

    def add_error(self, event: RunLogEvent, harness_event: HarnessEvent) -> None:
        failure = harness_event.failure
        self.steps.append(
            RunStep(
                sequence=event.sequence,
                timestamp=event.timestamp,
                kind=RunStepKind.ERROR,
                title="Error",
                body=failure.message if failure is not None else harness_event.message,
                detail=failure.fix if failure is not None else None,
                status=harness_event.status.value if harness_event.status else None,
                error=True,
            )
        )

    def add_status(self, event: RunLogEvent, title: str, body: str) -> None:
        self.steps.append(
            RunStep(
                sequence=event.sequence,
                timestamp=event.timestamp,
                kind=RunStepKind.STATUS,
                title=title,
                body=body,
            )
        )

    def matching_tool(self, harness_event: HarnessEvent) -> RunStep | None:
        if harness_event.tool_id is None:
            return None
        return self.tools.get(harness_event.tool_id)

    def replace_step(self, old: RunStep, new: RunStep) -> None:
        for index, step in enumerate(self.steps):
            if step is old:
                self.steps[index] = new
                break
        for tool_id, tool_step in tuple(self.tools.items()):
            if tool_step is old:
                self.tools[tool_id] = new


def actor_label(event: HarnessEvent) -> str | None:
    if event.actor is None:
        return None
    return event.actor.label


def status_title(message: str) -> str:
    return message.replace("_", " ").replace("-", " ").title()


def join_text(first: str | None, second: str) -> str:
    if first is None:
        return second
    if first.endswith("\n") or second.startswith("\n"):
        return f"{first}{second}"
    return f"{first}\n{second}"


def tool_title(event: HarnessEvent) -> str:
    display = event.tool_display
    if display is not None and (title := text_or_none(display.title)) is not None:
        return title
    if (name := text_or_none(event.tool_name)) is not None:
        return name
    return "Tool"


def tool_kind(event: HarnessEvent) -> str | None:
    display = event.tool_display
    if display is not None and display.kind is not None:
        return tool_kind_label(display.kind)
    return text_or_none(event.tool_name)


def tool_kind_label(kind: HarnessToolDisplayKind) -> str:
    return kind.value.replace("_", " ")


def tool_target(event: HarnessEvent) -> str | None:
    display = event.tool_display
    if display is None:
        return None
    return text_or_none(display.path or display.command or display.provider_thread_id)


def tool_status(event: HarnessEvent) -> str | None:
    display = event.tool_display
    if display is not None and display.status is not None:
        return display.status.value
    if event.tool_is_error is True:
        return "failed"
    if event.kind in {HarnessEventKind.TOOL_RESULT, HarnessEventKind.TOOL_SUMMARY}:
        return "completed"
    return None


def tool_summary(event: HarnessEvent) -> str | None:
    display = event.tool_display
    if display is not None and (summary := text_or_none(display.summary)) is not None:
        return summary
    if event.kind == HarnessEventKind.TOOL_USE:
        return text_or_none(event.message)
    if event.tool_result is not None:
        return value_preview(event.tool_result)
    return text_or_none(event.message)


def tool_detail(event: HarnessEvent) -> str | None:
    display = event.tool_display
    if display is None:
        return None
    details = [
        display.path,
        display.command,
        f"exit {display.exit_code}" if display.exit_code is not None else None,
        f"{display.duration_ms}ms" if display.duration_ms is not None else None,
    ]
    return text_or_none(" · ".join(detail for detail in details if detail))


def value_preview(value: Any) -> str:
    text = value if isinstance(value, str) else str(value)
    text = text.strip()
    if len(text) <= 280:
        return text
    return f"{text[:277]}..."


def text_or_none(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if text == "":
        return None
    return text


def agent_title(event: HarnessEvent) -> str:
    if event.kind == HarnessEventKind.AGENT_SPAWNED:
        return "Agent started"
    if event.kind == HarnessEventKind.AGENT_WAIT_STARTED:
        return "Waiting for agent"
    return "Agent finished"


def agent_status(event: HarnessEvent) -> str:
    if event.kind == HarnessEventKind.AGENT_COMPLETED:
        return "completed"
    if event.kind == HarnessEventKind.AGENT_WAIT_STARTED:
        return "waiting"
    return "started"
