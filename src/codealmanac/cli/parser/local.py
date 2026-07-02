import argparse

from codealmanac.services.control.models import ControlRunStatus
from codealmanac.services.harnesses.models import HarnessKind

LOCAL_DELIVERY_CHOICES = ("commit", "working-tree")
LOCAL_JOB_STATUS_CHOICES = tuple(status.value for status in ControlRunStatus)


def add_local_commands(subcommands: argparse._SubParsersAction) -> None:
    local = subcommands.add_parser("local", help="manage local CodeAlmanac setup")
    local_subcommands = local.add_subparsers(dest="local_command", required=True)

    status = local_subcommands.add_parser("status", help="show local setup status")
    status.add_argument("--json", action="store_true")

    update = local_subcommands.add_parser("update", help="run a local update now")
    update.add_argument(
        "--using",
        default=HarnessKind.CODEX.value,
        choices=tuple(kind.value for kind in HarnessKind),
    )
    update.add_argument("--json", action="store_true")

    setup = local_subcommands.add_parser(
        "setup",
        help="configure local repo automation for this checkout",
    )
    setup.add_argument("--branch", help="branch to maintain; defaults to current")
    setup.add_argument(
        "--delivery",
        choices=LOCAL_DELIVERY_CHOICES,
        default="commit",
        help="how local runs deliver wiki updates",
    )
    setup.add_argument(
        "--root",
        help="repo-relative Almanac root to maintain; defaults to almanac",
    )
    setup.add_argument(
        "--skip-hooks",
        action="store_true",
        help="record policy without installing Git hooks",
    )
    setup.add_argument("--json", action="store_true")

    triggers = local_subcommands.add_parser(
        "triggers",
        help="manage local branch trigger policy",
    )
    triggers_subcommands = triggers.add_subparsers(
        dest="triggers_command",
        required=True,
    )

    triggers_list = triggers_subcommands.add_parser(
        "list",
        help="list local branch trigger policies",
    )
    triggers_list.add_argument("--json", action="store_true")

    triggers_enable = triggers_subcommands.add_parser(
        "enable",
        help="enable local updates for a branch",
    )
    triggers_enable.add_argument("branch")
    triggers_enable.add_argument("--delivery", choices=LOCAL_DELIVERY_CHOICES)
    triggers_enable.add_argument("--json", action="store_true")

    triggers_disable = triggers_subcommands.add_parser(
        "disable",
        help="disable local updates for a branch",
    )
    triggers_disable.add_argument("branch")
    triggers_disable.add_argument("--json", action="store_true")

    delivery = local_subcommands.add_parser(
        "delivery",
        help="manage local delivery policy",
    )
    delivery_subcommands = delivery.add_subparsers(
        dest="delivery_command",
        required=True,
    )
    delivery_set = delivery_subcommands.add_parser(
        "set",
        help="set local delivery mode for a branch",
    )
    delivery_set.add_argument("--branch", required=True)
    delivery_set.add_argument("--mode", choices=LOCAL_DELIVERY_CHOICES, required=True)
    delivery_set.add_argument("--json", action="store_true")

    jobs = local_subcommands.add_parser("jobs", help="inspect local jobs")
    jobs_subcommands = jobs.add_subparsers(dest="jobs_command", required=True)

    jobs_list = jobs_subcommands.add_parser("list", help="list local jobs")
    jobs_list.add_argument("--limit", type=int, default=20)
    jobs_list.add_argument(
        "--status",
        action="append",
        choices=LOCAL_JOB_STATUS_CHOICES,
        default=[],
    )
    jobs_list.add_argument("--repository-id")
    jobs_list.add_argument("--branch-id")
    jobs_list.add_argument("--json", action="store_true")

    jobs_show = jobs_subcommands.add_parser("show", help="show a local job")
    jobs_show.add_argument("run_id")
    jobs_show.add_argument("--json", action="store_true")

    jobs_logs = jobs_subcommands.add_parser("logs", help="show local job logs")
    jobs_logs.add_argument("run_id")
    jobs_logs.add_argument("--json", action="store_true")
