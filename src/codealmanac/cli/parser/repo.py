import argparse

from codealmanac.cli.parser.cloud_auth import add_api_url

CLOUD_DELIVERY_CHOICES = ("commit", "pr")


def add_repo_commands(subcommands: argparse._SubParsersAction) -> None:
    repo = subcommands.add_parser("repo", help="manage the current cloud repository")
    repo_subcommands = repo.add_subparsers(dest="repo_command", required=True)

    status = repo_subcommands.add_parser("status", help="show cloud repo status")
    add_api_url(status)
    status.add_argument("--json", action="store_true")

    triggers = repo_subcommands.add_parser(
        "triggers",
        help="manage cloud branch trigger policy",
    )
    triggers_subcommands = triggers.add_subparsers(
        dest="triggers_command",
        required=True,
    )

    triggers_list = triggers_subcommands.add_parser(
        "list",
        help="list cloud branch trigger policies",
    )
    add_api_url(triggers_list)
    triggers_list.add_argument("--json", action="store_true")

    triggers_enable = triggers_subcommands.add_parser(
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

    triggers_disable = triggers_subcommands.add_parser(
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
    delivery_subcommands = delivery.add_subparsers(
        dest="delivery_command",
        required=True,
    )
    delivery_set = delivery_subcommands.add_parser(
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
