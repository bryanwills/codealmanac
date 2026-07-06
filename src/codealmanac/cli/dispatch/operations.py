import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.dispatch.config import load_cli_config, resolve_harness
from codealmanac.cli.render.root import (
    render_run_queue_start,
    render_scheduled_garden,
)
from codealmanac.workflows.garden.requests import GardenRequest
from codealmanac.workflows.ingest.requests import IngestRequest
from codealmanac.workflows.run_queue import ScheduledGardenRequest


def dispatch_ingest(args: argparse.Namespace, app: CodeAlmanac) -> int:
    cli_config = load_cli_config(app, args.wiki)
    request = IngestRequest(
        cwd=Path.cwd(),
        wiki=args.wiki,
        inputs=tuple(args.inputs),
        harness=resolve_harness(args.using, cli_config),
        title=args.title,
        guidance=args.guidance,
        auto_commit=cli_config.auto_commit,
    )
    result = app.workflows.queue.start_ingest(request)
    render_run_queue_start(result, json_output=args.json)
    return 0


def dispatch_garden(args: argparse.Namespace, app: CodeAlmanac) -> int:
    cli_config = load_cli_config(app, args.wiki)
    request = GardenRequest(
        cwd=Path.cwd(),
        wiki=args.wiki,
        harness=resolve_harness(args.using, cli_config),
        title=args.title,
        guidance=args.guidance,
        auto_commit=cli_config.auto_commit,
    )
    result = app.workflows.queue.start_garden(request)
    render_run_queue_start(result, json_output=args.json)
    return 0


def dispatch_scheduled_garden(args: argparse.Namespace, app: CodeAlmanac) -> int:
    cli_config = app.config.load_user()
    result = app.workflows.queue.start_scheduled_garden(
        ScheduledGardenRequest(
            harness=cli_config.harness.default,
            auto_commit=cli_config.auto_commit,
        )
    )
    render_scheduled_garden(result)
    return 0
