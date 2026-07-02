import argparse

LOCAL_DELIVERY_CHOICES = ("commit", "working-tree")


def add_local_commands(subcommands: argparse._SubParsersAction) -> None:
    local = subcommands.add_parser("local", help="manage local CodeAlmanac setup")
    local_subcommands = local.add_subparsers(dest="local_command", required=True)

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
