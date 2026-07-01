import argparse
from datetime import timedelta
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.dispatch.automation import resolve_automation_quiet
from codealmanac.cli.dispatch.config import (
    load_cli_config,
    parse_optional_duration,
)
from codealmanac.cli.render.admin import render_setup_result, render_uninstall_result
from codealmanac.services.config.models import CodeAlmanacConfig
from codealmanac.services.setup.models import SetupTarget
from codealmanac.services.setup.requests import RunSetupRequest, RunUninstallRequest


def dispatch_setup(args: argparse.Namespace, app: CodeAlmanac) -> int:
    install_automation = should_setup_install_automation(args)
    cli_config = load_cli_config(app, None) if install_automation else None
    result = app.setup.run(
        RunSetupRequest(
            cwd=Path.cwd(),
            targets=parse_setup_targets(args.target),
            yes=args.yes,
            skip_instructions=args.skip_instructions,
            install_automation=install_automation,
            sync_every=parse_optional_duration(args.sync_every, "--sync-every"),
            sync_quiet=resolve_setup_quiet(args.sync_quiet, cli_config),
            garden_every=parse_optional_duration(
                args.garden_every,
                "--garden-every",
            ),
            garden_off=args.garden_off,
        )
    )
    render_setup_result(result, json_output=args.json)
    return 0


def dispatch_uninstall(args: argparse.Namespace, app: CodeAlmanac) -> int:
    result = app.setup.uninstall(
        RunUninstallRequest(
            targets=parse_setup_targets(args.target),
            yes=args.yes,
            keep_instructions=args.keep_instructions,
            keep_automation=args.keep_automation,
        )
    )
    render_uninstall_result(result, json_output=args.json)
    return 0


def resolve_setup_quiet(
    value: str | None,
    config: CodeAlmanacConfig | None,
) -> timedelta | None:
    if config is None:
        return None
    return resolve_automation_quiet(value, config)


def should_setup_install_automation(args: argparse.Namespace) -> bool:
    return (
        args.install_automation
        or args.sync_every is not None
        or args.sync_quiet is not None
        or args.garden_every is not None
        or args.garden_off
    )


def parse_setup_targets(value: str) -> tuple[SetupTarget, ...]:
    if value == "all":
        return (SetupTarget.CODEX, SetupTarget.CLAUDE)
    return (SetupTarget(value),)
