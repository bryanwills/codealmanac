import argparse

from codealmanac.services.automation.models import AutomationTask


def add_admin_commands(subcommands: argparse._SubParsersAction) -> None:
    setup = subcommands.add_parser("setup", help="set up local agent instructions")
    setup.add_argument(
        "--target",
        choices=("all", "codex", "claude"),
        default="all",
        help="agent instruction target to configure",
    )
    setup.add_argument("--yes", action="store_true", help="run without prompts")
    setup.add_argument(
        "--skip-instructions",
        action="store_true",
        help="skip global agent instruction installation",
    )
    setup.add_argument(
        "--install-automation",
        action="store_true",
        help="install scheduled sync and garden automation during setup",
    )
    setup.add_argument(
        "--sync-every",
        help="scheduled sync interval when setup installs automation",
    )
    setup.add_argument(
        "--sync-quiet",
        help="minimum quiet time before scheduled sync",
    )
    setup.add_argument(
        "--garden-every",
        help="scheduled Garden interval when setup installs automation",
    )
    setup.add_argument(
        "--garden-off",
        action="store_true",
        help="install scheduled sync without scheduled Garden",
    )
    setup.add_argument("--json", action="store_true")

    uninstall = subcommands.add_parser(
        "uninstall",
        help="remove setup-owned local artifacts",
    )
    uninstall.add_argument(
        "--target",
        choices=("all", "codex", "claude"),
        default="all",
        help="agent instruction target to remove",
    )
    uninstall.add_argument("--yes", action="store_true", help="run without prompts")
    uninstall.add_argument(
        "--keep-instructions",
        action="store_true",
        help="leave global agent instructions installed",
    )
    uninstall.add_argument(
        "--keep-automation",
        action="store_true",
        help="leave scheduled automation installed",
    )
    uninstall.add_argument("--json", action="store_true")

    doctor = subcommands.add_parser("doctor", help="check local install and wiki")
    doctor.add_argument("--wiki")
    doctor.add_argument("--json", action="store_true")

    update = subcommands.add_parser("update", help="update the local CLI")
    update.add_argument("--check", action="store_true")
    update.add_argument("--json", action="store_true")

    jobs = subcommands.add_parser("jobs", help="inspect local lifecycle jobs")
    jobs.add_argument("--wiki")
    jobs.add_argument("--limit", type=int)
    jobs.add_argument("--json", action="store_true")
    job_subcommands = jobs.add_subparsers(dest="jobs_command")
    jobs_show = job_subcommands.add_parser("show", help="show one job record")
    jobs_show.add_argument("run_id")
    jobs_show.add_argument("--json", action="store_true")
    jobs_logs = job_subcommands.add_parser("logs", help="show one job log")
    jobs_logs.add_argument("run_id")
    jobs_logs.add_argument("--json", action="store_true")
    jobs_attach = job_subcommands.add_parser("attach", help="attach to one job log")
    jobs_attach.add_argument("run_id")
    jobs_attach.add_argument("--json", action="store_true")
    jobs_cancel = job_subcommands.add_parser("cancel", help="cancel one queued job")
    jobs_cancel.add_argument("run_id")
    jobs_cancel.add_argument("--json", action="store_true")

    automation = subcommands.add_parser(
        "automation",
        help="manage local scheduled automation",
    )
    automation_subcommands = automation.add_subparsers(
        dest="automation_command",
        required=True,
    )
    automation_install = automation_subcommands.add_parser(
        "install",
        help="install scheduled sync and garden jobs",
    )
    automation_install.add_argument(
        "tasks",
        nargs="*",
        choices=tuple(task.value for task in AutomationTask),
    )
    automation_install.add_argument(
        "--every",
        help="run interval for sync or one selected task",
    )
    automation_install.add_argument(
        "--quiet",
        help="minimum quiet time before sync",
    )
    automation_install.add_argument(
        "--garden-every",
        help="Garden run interval (default: 4h)",
    )
    automation_install.add_argument(
        "--garden-off",
        action="store_true",
        help="disable scheduled Garden automation",
    )
    automation_install.add_argument("--json", action="store_true")
    automation_uninstall = automation_subcommands.add_parser(
        "uninstall",
        help="remove scheduled jobs",
    )
    automation_uninstall.add_argument(
        "tasks",
        nargs="*",
        choices=tuple(task.value for task in AutomationTask),
    )
    automation_uninstall.add_argument("--json", action="store_true")
    automation_status = automation_subcommands.add_parser(
        "status",
        help="show scheduled automation status",
    )
    automation_status.add_argument(
        "tasks",
        nargs="*",
        choices=tuple(task.value for task in AutomationTask),
    )
    automation_status.add_argument("--json", action="store_true")
