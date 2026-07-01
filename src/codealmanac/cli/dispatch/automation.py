import argparse
from collections.abc import Sequence
from datetime import timedelta
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.dispatch.config import (
    load_cli_config,
    parse_optional_duration,
)
from codealmanac.cli.render.admin import (
    render_automation_install,
    render_automation_status,
    render_automation_uninstall,
)
from codealmanac.services.automation.models import AutomationTask
from codealmanac.services.automation.requests import (
    AutomationStatusRequest,
    InstallAutomationRequest,
    UninstallAutomationRequest,
)
from codealmanac.services.config.models import CodeAlmanacConfig


def dispatch_automation(args: argparse.Namespace, app: CodeAlmanac) -> int:
    tasks = parse_automation_tasks(args.tasks)
    if args.automation_command == "install":
        cli_config = load_cli_config(app, None)
        result = app.automation.install(
            InstallAutomationRequest(
                cwd=Path.cwd(),
                tasks=tasks,
                every=parse_optional_duration(args.every, "--every"),
                quiet=resolve_automation_quiet(args.quiet, cli_config),
                garden_every=parse_optional_duration(
                    args.garden_every,
                    "--garden-every",
                ),
                garden_off=args.garden_off,
            )
        )
        render_automation_install(result, json_output=args.json)
        return 0
    if args.automation_command == "uninstall":
        result = app.automation.uninstall(UninstallAutomationRequest(tasks=tasks))
        render_automation_uninstall(result, json_output=args.json)
        return 0
    if args.automation_command == "status":
        result = app.automation.status(AutomationStatusRequest(tasks=tasks))
        render_automation_status(result, json_output=args.json)
        return 0
    raise AssertionError(f"unhandled automation command: {args.automation_command}")


def resolve_automation_quiet(
    value: str | None,
    config: CodeAlmanacConfig,
) -> timedelta:
    if value is None:
        return config.sync.quiet
    parsed = parse_optional_duration(value, "--quiet")
    if parsed is None:
        raise AssertionError("parsed automation quiet is unexpectedly empty")
    return parsed


def parse_automation_tasks(values: Sequence[str]) -> tuple[AutomationTask, ...]:
    tasks: list[AutomationTask] = []
    for value in values:
        task = AutomationTask(value)
        if task not in tasks:
            tasks.append(task)
    return tuple(tasks)
