import argparse


def add_config_commands(subcommands: argparse._SubParsersAction) -> None:
    config = subcommands.add_parser("config", help="manage config")
    config_subcommands = config.add_subparsers(dest="config_command", required=True)
    set_parser = config_subcommands.add_parser("set", help="set a user config value")
    set_parser.add_argument("key", choices=("auto_commit",))
    set_parser.add_argument("value", choices=("true", "false"))
