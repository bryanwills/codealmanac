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
    render_doctor,
    render_run,
    render_run_log,
    render_runs,
    render_update_plan,
    render_update_result,
)
from codealmanac.services.automation.models import AutomationTask
from codealmanac.services.automation.requests import (
    AutomationStatusRequest,
    InstallAutomationRequest,
    UninstallAutomationRequest,
)
from codealmanac.services.config.models import CodeAlmanacConfig
from codealmanac.services.diagnostics.requests import DoctorRequest
from codealmanac.services.runs.requests import (
    ListRunsRequest,
    ReadRunLogRequest,
    ShowRunRequest,
)
from codealmanac.services.updates.models import UpdateStatus
from codealmanac.services.updates.requests import CheckUpdateRequest, RunUpdateRequest

ADMIN_COMMANDS = frozenset(("automation", "doctor", "jobs", "update"))


def is_admin_command(command: str | None) -> bool:
    return command in ADMIN_COMMANDS


def dispatch_admin(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.command == "doctor":
        report = app.diagnostics.check(DoctorRequest(cwd=Path.cwd(), wiki=args.wiki))
        render_doctor(report, json_output=args.json)
        return 0
    if args.command == "update":
        if args.check:
            plan = app.updates.check(CheckUpdateRequest())
            render_update_plan(plan, json_output=args.json)
            return 0
        result = app.updates.run(RunUpdateRequest())
        render_update_result(result, json_output=args.json)
        return 0 if result.status == UpdateStatus.COMPLETED else 1
    if args.command == "jobs":
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
        records = app.runs.list(
            ListRunsRequest(cwd=Path.cwd(), wiki=args.wiki, limit=args.limit)
        )
        render_runs(records, json_output=args.json)
        return 0
    if args.command == "automation":
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
    raise AssertionError(f"unhandled admin command: {args.command}")


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
