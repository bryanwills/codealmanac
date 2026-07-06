import argparse

from codealmanac.app import CodeAlmanac
from codealmanac.cli.dispatch.automation import dispatch_automation
from codealmanac.cli.dispatch.config_command import dispatch_config
from codealmanac.cli.dispatch.diagnostics import dispatch_doctor
from codealmanac.cli.dispatch.jobs import dispatch_jobs
from codealmanac.cli.dispatch.setup import dispatch_setup, dispatch_uninstall
from codealmanac.cli.dispatch.updates import dispatch_update

ADMIN_COMMANDS = frozenset(
    ("automation", "config", "doctor", "jobs", "setup", "uninstall", "update")
)


def is_admin_command(command: str | None) -> bool:
    return command in ADMIN_COMMANDS


def dispatch_admin(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.command == "setup":
        return dispatch_setup(args, app)
    if args.command == "uninstall":
        return dispatch_uninstall(args, app)
    if args.command == "config":
        return dispatch_config(args, app)
    if args.command == "doctor":
        return dispatch_doctor(args, app)
    if args.command == "update":
        return dispatch_update(args, app)
    if args.command == "jobs":
        return dispatch_jobs(args, app)
    if args.command == "automation":
        return dispatch_automation(args, app)
    raise AssertionError(f"unhandled admin command: {args.command}")
