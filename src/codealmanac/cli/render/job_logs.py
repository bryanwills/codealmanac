import json
import sys
from collections.abc import Iterable

from codealmanac.cli.render.common import print_json_model
from codealmanac.cli.render.jobs import status_label
from codealmanac.cli.render.style import style
from codealmanac.services.runs.models import (
    RunAttachSnapshot,
    RunAttachUpdate,
    RunLogEvent,
    RunRecord,
    RunStatus,
)
from codealmanac.services.runs.transcript import RunStep, RunStepKind, project_run_steps


def render_run_log(events: tuple[RunLogEvent, ...], json_output: bool) -> None:
    steps = project_run_steps(events)
    if json_output:
        data = [step.model_dump(mode="json", exclude_none=True) for step in steps]
        print(json.dumps(data, indent=2))
        return
    for step in steps:
        render_run_step(step)


def render_run_attach(snapshot: RunAttachSnapshot, json_output: bool) -> None:
    if json_output:
        print_json_model(snapshot)
        return
    render_run_log(snapshot.events, json_output=False)
    if len(snapshot.events) == 0:
        print("no log events")
    print_terminal_status(snapshot.record)


def render_run_attach_stream(
    updates: Iterable[RunAttachUpdate],
    json_output: bool,
) -> None:
    saw_event = False
    for update in updates:
        if json_output:
            print(update.model_dump_json(exclude_none=True))
            sys.stdout.flush()
            continue
        steps = project_run_steps(update.events)
        for step in steps:
            render_run_step(step)
            saw_event = True
        if update.terminal:
            if not saw_event:
                print("no log events")
            print_terminal_status(update.record)
        sys.stdout.flush()


def print_terminal_status(record: RunRecord) -> None:
    print(f"status: {status_label(record.status)}")
    if record.status == RunStatus.FAILED and record.error is not None:
        print(f"{style.RED}error:{style.RST} {record.error}")
    if record.status == RunStatus.DONE and record.summary is not None:
        print(f"summary: {record.summary}")


def render_run_step(step: RunStep) -> None:
    sequence = f"{style.DIM}{step.sequence:>4}{style.RST}"
    kind = step_kind_label(step)
    print(f"{sequence}  {kind}  {step.title}")
    if step.body:
        print_indented(step.body)
    meta = step_meta(step)
    if meta:
        print(f"      {style.DIM}{meta}{style.RST}")


def step_kind_label(step: RunStep) -> str:
    if step.error or step.kind == RunStepKind.ERROR:
        return f"{style.RED}error{style.RST}"
    if step.kind == RunStepKind.TOOL:
        return f"{style.BLUE}tool{style.RST}"
    if step.kind == RunStepKind.AGENT:
        return f"{style.BLUE}agent{style.RST}"
    if step.kind == RunStepKind.STATUS:
        return f"{style.DIM}status{style.RST}"
    return f"{style.BLUE}text{style.RST}"


def step_meta(step: RunStep) -> str:
    parts = [
        step.status,
        step.tool,
        step.target,
        step.detail,
    ]
    return " · ".join(part for part in parts if part)


def print_indented(value: str) -> None:
    for line in value.splitlines() or [value]:
        print(f"      {line}")
