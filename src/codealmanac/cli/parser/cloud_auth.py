import argparse

from codealmanac.services.cloud_auth.models import DEFAULT_CLOUD_API_URL


def add_cloud_auth_commands(subcommands: argparse._SubParsersAction) -> None:
    login = subcommands.add_parser("login", help="sign in to CodeAlmanac cloud")
    add_api_url(login)
    login.add_argument(
        "--no-browser",
        action="store_true",
        help="print the login URL without opening a browser",
    )
    login.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="seconds to wait for browser approval",
    )
    login.add_argument(
        "--poll-every",
        type=float,
        default=2.0,
        help="seconds between login polling attempts",
    )
    login.add_argument(
        "--force",
        action="store_true",
        help="start a fresh login even when already signed in",
    )
    login.add_argument("--json", action="store_true")

    whoami = subcommands.add_parser("whoami", help="show the signed-in cloud identity")
    add_api_url(whoami)
    whoami.add_argument("--json", action="store_true")

    logout = subcommands.add_parser("logout", help="sign out of CodeAlmanac cloud")
    add_api_url(logout)
    logout.add_argument("--json", action="store_true")


def add_api_url(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--api-url",
        default=DEFAULT_CLOUD_API_URL,
        help="CodeAlmanac cloud API URL",
    )
