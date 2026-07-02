import argparse

from codealmanac.services.cloud_auth.models import DEFAULT_CLOUD_APP_URL


def add_open_commands(subcommands: argparse._SubParsersAction) -> None:
    open_command = subcommands.add_parser(
        "open",
        help="open the current cloud wiki",
    )
    add_app_url(open_command)
    add_browser_flags(open_command)


def add_app_url(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--app-url", default=DEFAULT_CLOUD_APP_URL)


def add_browser_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--json", action="store_true")
