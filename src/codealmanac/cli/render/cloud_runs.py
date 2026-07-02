import json
import sys

from codealmanac.cli.render.common import print_json_model
from codealmanac.services.cloud_runs.models import CloudRun, CloudRunEvent
from codealmanac.workflows.cloud_runs.models import (
    CloudRunDetailResult,
    CloudRunListResult,
    CloudRunLogResult,
)


def render_cloud_runs(result: CloudRunListResult, *, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    if len(result.page.items) == 0:
        print("# 0 cloud runs", file=sys.stderr)
        return
    for run in result.page.items:
        print(cloud_run_row(run))
    if result.page.next_cursor is not None:
        print(f"next_cursor: {result.page.next_cursor}", file=sys.stderr)


def render_cloud_run(result: CloudRunDetailResult, *, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    run = result.run
    print(f"id: {run.run_id}")
    print(f"repo_id: {run.repo_id}")
    print(f"status: {run.status}")
    print(f"source: {run.source.label}")
    if run.summary is not None:
        print(f"summary: {run.summary}")
    if len(run.files_changed) > 0:
        print("files_changed:")
        for path in run.files_changed:
            print(f"- {path}")
    if run.commit_sha is not None:
        print(f"commit_sha: {run.commit_sha}")
    if run.created_at is not None:
        print(f"created_at: {run.created_at.isoformat()}")
    if run.finished_at is not None:
        print(f"finished_at: {run.finished_at.isoformat()}")


def render_cloud_run_log(result: CloudRunLogResult, *, json_output: bool) -> None:
    if json_output:
        data = [
            event.model_dump(mode="json", exclude_none=True) for event in result.events
        ]
        print(json.dumps(data, indent=2))
        return
    if len(result.events) == 0:
        print("no log events")
        return
    for event in result.events:
        print(cloud_run_event_row(event))


def cloud_run_row(run: CloudRun) -> str:
    summary = run.summary or ""
    return f"{run.run_id}\t{run.status}\t{run.source.label}\t{summary}"


def cloud_run_event_row(event: CloudRunEvent) -> str:
    return f"{event.sequence}\t{event.kind}\t{event.message}"
