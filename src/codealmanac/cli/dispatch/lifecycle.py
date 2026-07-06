import argparse

from codealmanac.app import CodeAlmanac
from codealmanac.cli.dispatch.build import dispatch_init
from codealmanac.cli.dispatch.operations import (
    dispatch_garden,
    dispatch_ingest,
    dispatch_scheduled_garden,
)
from codealmanac.cli.dispatch.sync import dispatch_sync
from codealmanac.cli.dispatch.worker import dispatch_run_worker

LIFECYCLE_COMMANDS = frozenset(
    ("__garden-scheduler", "__run-worker", "garden", "ingest", "init", "sync")
)


def is_lifecycle_command(command: str | None) -> bool:
    return command in LIFECYCLE_COMMANDS


def dispatch_lifecycle(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.command == "init":
        return dispatch_init(args, app)
    if args.command == "ingest":
        return dispatch_ingest(args, app)
    if args.command == "garden":
        return dispatch_garden(args, app)
    if args.command == "__run-worker":
        return dispatch_run_worker(args, app)
    if args.command == "__garden-scheduler":
        return dispatch_scheduled_garden(args, app)
    if args.command == "sync":
        return dispatch_sync(args, app)
    raise AssertionError(f"unhandled lifecycle command: {args.command}")
