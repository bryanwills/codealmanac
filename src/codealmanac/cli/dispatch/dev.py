import argparse

from codealmanac.app import CodeAlmanac
from codealmanac.cli.dispatch.operations import dispatch_garden, dispatch_ingest

DEV_COMMANDS = frozenset(("dev",))


def is_dev_command(command: str | None) -> bool:
    return command in DEV_COMMANDS


def dispatch_dev(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.dev_command == "ingest":
        return dispatch_ingest(args, app)
    if args.dev_command == "garden":
        return dispatch_garden(args, app)
    raise AssertionError(f"unhandled dev command: {args.dev_command}")
