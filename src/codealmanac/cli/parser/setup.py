import argparse

SETUP_TARGETS = ("all", "codex", "claude")


def add_setup_commands(subcommands: argparse._SubParsersAction) -> None:
    setup = subcommands.add_parser("setup", help="set up local agent instructions")
    setup.add_argument(
        "--target",
        choices=SETUP_TARGETS,
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
        choices=SETUP_TARGETS,
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
