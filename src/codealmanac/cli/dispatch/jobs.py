import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.render.admin import (
    render_run,
    render_run_attach,
    render_run_cancel,
    render_run_log,
    render_runs,
)
from codealmanac.services.runs.requests import (
    AttachRunRequest,
    CancelRunRequest,
    ListRunsRequest,
    ReadRunLogRequest,
    ShowRunRequest,
)


def dispatch_jobs(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.jobs_command == "show":
        record = app.runs.show(
            ShowRunRequest(cwd=Path.cwd(), wiki=args.wiki, run_id=args.run_id)
        )
        render_run(record, json_output=args.json)
        return 0
    if args.jobs_command == "logs":
        events = app.runs.log(
            ReadRunLogRequest(cwd=Path.cwd(), wiki=args.wiki, run_id=args.run_id)
        )
        render_run_log(events, json_output=args.json)
        return 0
    if args.jobs_command == "attach":
        snapshot = app.runs.attach(
            AttachRunRequest(cwd=Path.cwd(), wiki=args.wiki, run_id=args.run_id)
        )
        render_run_attach(snapshot, json_output=args.json)
        return 0
    if args.jobs_command == "cancel":
        result = app.runs.cancel(
            CancelRunRequest(cwd=Path.cwd(), wiki=args.wiki, run_id=args.run_id)
        )
        render_run_cancel(result, json_output=args.json)
        return 0
    records = app.runs.list(
        ListRunsRequest(cwd=Path.cwd(), wiki=args.wiki, limit=args.limit)
    )
    render_runs(records, json_output=args.json)
    return 0
