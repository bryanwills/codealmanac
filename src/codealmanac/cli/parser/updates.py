import argparse


def add_update_commands(subcommands: argparse._SubParsersAction) -> None:
    update = subcommands.add_parser("update", help="update the local CLI")
    update.add_argument("--check", action="store_true")
    update.add_argument("--json", action="store_true")
