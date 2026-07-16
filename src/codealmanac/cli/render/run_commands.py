import json

from codealmanac.cli.render.style import style
from codealmanac.cli.render.terminal import card_row, terminal_width, visible_length
from codealmanac.services.runs.models import RunKind
from codealmanac.workflows.run_queue.models import (
    RunQueueStartResult,
    ScheduledGardenResult,
)

RUN_HEADLINES = {
    RunKind.BUILD: "Building your CodeAlmanac in the background",
    RunKind.INGEST: "Adding knowledge to your CodeAlmanac in the background",
    RunKind.GARDEN: "Improving your CodeAlmanac in the background",
}


def render_run_queue_start(
    result: RunQueueStartResult,
    json_output: bool,
) -> None:
    if json_output:
        print(
            json.dumps(
                {
                    "run_id": result.run.run_id,
                    "repository": result.repository.name,
                    "runs_ahead": result.runs_ahead,
                    "status": result.run.status.value,
                    "child_pid": result.worker.child_pid,
                },
                indent=2,
            )
        )
        return
    render_run_queue_started(result)


def render_run_queue_started(result: RunQueueStartResult) -> None:
    record = result.run
    blue = style.BLUE
    dim = style.DIM
    bold = style.BOLD
    rst = style.RST
    headline = RUN_HEADLINES[record.kind]
    print(f"{blue}◆{rst} {bold}{headline}{rst}")
    print()
    render_viewer_follow_box()
    print()
    print("  Prefer the terminal?")
    print(f"    {bold}codealmanac jobs attach {record.run_id}{rst}")
    print()
    print(
        f"{dim}  Job: {record.run_id} · Repo: {result.repository.name}{rst}"
    )


def render_viewer_follow_box() -> None:
    blue = style.BLUE
    dim = style.DIM
    bold = style.BOLD
    rst = style.RST
    border = f"{blue}{dim}"
    lines = (
        f"  {bold}Follow progress in the CodeAlmanac viewer{rst}",
        "",
        f"    {blue}{bold}codealmanac serve{rst}",
        "",
        f"  Then select {bold}Jobs{rst} in the sidebar.",
    )
    available_width = max(40, terminal_width() - 6)
    content_width = max(visible_length(line) for line in lines)
    width = max(content_width, min(62, available_width))
    print(f"  {border}╭{'─' * width}╮{rst}")
    print(f"  {card_row('', width, border, rst)}")
    for line in lines:
        print(f"  {card_row(line, width, border, rst)}")
    print(f"  {card_row('', width, border, rst)}")
    print(f"  {border}╰{'─' * width}╯{rst}")


def render_scheduled_garden(result: ScheduledGardenResult) -> None:
    print(f"scheduled garden: {len(result.runs)} queued, {len(result.skipped)} skipped")
    for run in result.runs:
        print(f"  - {run.kind.value} {run.run_id}")
    for repository in result.skipped:
        print(f"  - skipped {repository.name}: garden already queued or running")
    if result.worker is not None:
        print(f"worker: pid {result.worker.child_pid}")
    if result.worker_error is not None:
        print(f"  ! worker spawn failed: {result.worker_error}")
