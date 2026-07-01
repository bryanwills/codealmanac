import json
import sys

from codealmanac.cli.render.common import print_json_model, print_json_rows
from codealmanac.services.runs.models import (
    RunAttachSnapshot,
    RunCancelResult,
    RunLogEvent,
    RunRecord,
)


def render_runs(records: tuple[RunRecord, ...], json_output: bool) -> None:
    if json_output:
        print_json_rows(records)
        return
    if len(records) == 0:
        print("# 0 jobs", file=sys.stderr)
        return
    for record in records:
        title = record.title or ""
        print(
            f"{record.run_id}\t{record.status.value}\t"
            f"{record.operation.value}\t{title}"
        )


def render_run(record: RunRecord, json_output: bool) -> None:
    if json_output:
        print_json_model(record)
        return
    print(f"id: {record.run_id}")
    print(f"operation: {record.operation.value}")
    print(f"status: {record.status.value}")
    if record.title is not None:
        print(f"title: {record.title}")
    if record.summary is not None:
        print(f"summary: {record.summary}")
    if record.error is not None:
        print(f"error: {record.error}")
    if record.harness_transcript is not None:
        print(
            "harness_transcript: "
            f"{record.harness_transcript.kind.value} "
            f"{record.harness_transcript.session_id}"
        )
        if record.harness_transcript.transcript_path is not None:
            print(
                "harness_transcript_path: "
                f"{record.harness_transcript.transcript_path}"
            )
    print(f"created_at: {record.created_at.isoformat()}")
    print(f"updated_at: {record.updated_at.isoformat()}")


def render_run_log(events: tuple[RunLogEvent, ...], json_output: bool) -> None:
    if json_output:
        data = [event.model_dump(mode="json", exclude_none=True) for event in events]
        print(json.dumps(data, indent=2))
        return
    for event in events:
        print(f"{event.sequence}\t{event.kind.value}\t{event.message}")


def render_run_attach(snapshot: RunAttachSnapshot, json_output: bool) -> None:
    if json_output:
        print_json_model(snapshot)
        return
    render_run_log(snapshot.events, json_output=False)
    if len(snapshot.events) == 0:
        print("no log events")
    print(f"status: {snapshot.record.status.value}")


def render_run_cancel(result: RunCancelResult, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    if result.changed:
        print(f"cancelled {result.record.run_id}")
        return
    print(f"job already {result.record.status.value}: {result.record.run_id}")
