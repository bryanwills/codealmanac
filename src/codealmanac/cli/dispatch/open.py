import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.render.cloud_open import render_cloud_open
from codealmanac.cloud.open.requests import OpenCloudTargetRequest

OPEN_COMMANDS = frozenset(("open",))


def is_open_command(command: str | None) -> bool:
    return command in OPEN_COMMANDS


def dispatch_default_open(args: argparse.Namespace, app: CodeAlmanac) -> int:
    result = app.workflows.cloud_open.open(OpenCloudTargetRequest(cwd=Path.cwd()))
    render_cloud_open(result, json_output=False)
    return 0


def dispatch_open(args: argparse.Namespace, app: CodeAlmanac) -> int:
    result = app.workflows.cloud_open.open(
        OpenCloudTargetRequest(
            cwd=Path.cwd(),
            app_url=args.app_url,
            no_browser=args.no_browser,
        )
    )
    render_cloud_open(result, json_output=args.json)
    return 0
