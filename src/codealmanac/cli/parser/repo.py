import argparse

from codealmanac.cli.parser.cloud_auth import add_api_url
from codealmanac.cli.parser.open import add_app_url, add_browser_flags

CLOUD_DELIVERY_CHOICES = ("commit", "pr")
REPO_OPEN_TARGET_CHOICES = ("activity", "settings", "github", "github-app")


def add_repo_commands(subcommands: argparse._SubParsersAction) -> None:
    repo = subcommands.add_parser("repo", help="manage the current cloud repository")
    repo_subcommands = repo.add_subparsers(dest="repo_command", required=True)

    repo_list = repo_subcommands.add_parser("list", help="list cloud repositories")
    repo_list.add_argument("--limit", type=int)
    repo_list.add_argument("--cursor")
    add_api_url(repo_list)
    repo_list.add_argument("--json", action="store_true")

    setup = repo_subcommands.add_parser(
        "setup",
        help="open cloud setup for the current repository",
    )
    add_app_url(setup)
    add_browser_flags(setup)

    open_command = repo_subcommands.add_parser(
        "open",
        help="open cloud or GitHub pages for the current repository",
    )
    open_command.add_argument(
        "target",
        nargs="?",
        choices=REPO_OPEN_TARGET_CHOICES,
        default="activity",
    )
    add_app_url(open_command)
    add_browser_flags(open_command)

    status = repo_subcommands.add_parser("status", help="show cloud repo status")
    add_api_url(status)
    status.add_argument("--json", action="store_true")

    triggers = repo_subcommands.add_parser(
        "triggers",
        help="manage cloud branch trigger policy",
    )
    trigger_sub = triggers.add_subparsers(dest="triggers_command", required=True)

    triggers_list = trigger_sub.add_parser(
        "list",
        help="list cloud branch trigger policies",
    )
    add_api_url(triggers_list)
    triggers_list.add_argument("--json", action="store_true")

    triggers_enable = trigger_sub.add_parser(
        "enable",
        help="enable cloud updates for a branch",
    )
    triggers_enable.add_argument("branch")
    triggers_enable.add_argument(
        "--delivery",
        choices=CLOUD_DELIVERY_CHOICES,
        required=True,
    )
    add_api_url(triggers_enable)
    triggers_enable.add_argument("--json", action="store_true")

    triggers_disable = trigger_sub.add_parser(
        "disable",
        help="disable cloud updates for a branch",
    )
    triggers_disable.add_argument("branch")
    add_api_url(triggers_disable)
    triggers_disable.add_argument("--json", action="store_true")

    delivery = repo_subcommands.add_parser(
        "delivery",
        help="manage cloud delivery policy",
    )
    delivery_sub = delivery.add_subparsers(dest="delivery_command", required=True)
    delivery_set = delivery_sub.add_parser(
        "set",
        help="set cloud delivery mode for a branch",
    )
    delivery_set.add_argument("--branch", required=True)
    delivery_set.add_argument(
        "--mode",
        choices=CLOUD_DELIVERY_CHOICES,
        required=True,
    )
    add_api_url(delivery_set)
    delivery_set.add_argument("--json", action="store_true")
