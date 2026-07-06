import argparse
import sys
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
from codealmanac.services.setup.models import (
    PackageUninstallStatus,
    SetupTarget,
    UninstallResult,
)
from codealmanac.services.setup.requests import RunSetupRequest, RunUninstallRequest


def dispatch_setup(args: argparse.Namespace, app: CodeAlmanac) -> int:
    cli_config = load_cli_config(app, None)
    result = app.setup.run(
        RunSetupRequest(
            cwd=Path.cwd(),
            targets=parse_setup_targets(args.target),
            yes=args.yes,
            auto_commit=not args.no_auto_commit,
            auto_update=not args.no_auto_update,
            skip_instructions=args.skip_instructions,
            sync_every=parse_optional_duration(args.sync_every, "--sync-every"),
            sync_quiet=resolve_setup_quiet(args.sync_quiet, cli_config),
            sync_off=args.sync_off,
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
    if not args.yes and not confirm_uninstall():
        return 1
    result = app.setup.uninstall(
        RunUninstallRequest(
            yes=args.yes,
        )
    )
    render_uninstall_result(result, json_output=args.json)
    return uninstall_exit_code(result)


def confirm_uninstall() -> bool:
    if not sys.stdin.isatty():
        print(
            "codealmanac uninstall requires --yes in non-interactive shells",
            file=sys.stderr,
        )
        return False
    response = input("Uninstall CodeAlmanac-owned machine artifacts? [y/N] ")
    if response.strip().casefold() in {"y", "yes"}:
        return True
    print("CodeAlmanac uninstall canceled.", file=sys.stderr)
    return False


def uninstall_exit_code(result: UninstallResult) -> int:
    if (
        result.package_uninstall is not None
        and result.package_uninstall.status == PackageUninstallStatus.FAILED
    ):
        return 1
    return 0


def resolve_setup_quiet(
    value: str | None,
    config: CodeAlmanacConfig | None,
) -> timedelta | None:
    if config is None:
        raise AssertionError("setup config is required")
    return resolve_automation_quiet(value, config)


def parse_setup_targets(value: str) -> tuple[SetupTarget, ...]:
    if value == "all":
        return (SetupTarget.CODEX, SetupTarget.CLAUDE)
    return (SetupTarget(value),)
