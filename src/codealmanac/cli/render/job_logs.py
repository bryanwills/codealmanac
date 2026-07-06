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


def render_run_log(events: tuple[RunLogEvent, ...], json_output: bool) -> None:
    if json_output:
        data = [event.model_dump(mode="json", exclude_none=True) for event in events]
        print(json.dumps(data, indent=2))
        return
    for event in events:
        render_run_log_event(event)


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
        for event in update.events:
            render_run_log_event(event)
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


def render_run_log_event(event: RunLogEvent) -> None:
    sequence = f"{style.DIM}{event.sequence:>4}{style.RST}"
    kind = f"{style.BLUE}{event.kind.value}{style.RST}"
    print(f"{sequence}  {kind}  {event.message}")
