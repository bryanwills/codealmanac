import argparse

from codealmanac.engine.harnesses.models import HarnessKind


def add_dev_commands(subcommands: argparse._SubParsersAction) -> None:
    dev = subcommands.add_parser("dev", help=argparse.SUPPRESS)
    dev_subcommands = dev.add_subparsers(dest="dev_command", required=True)

    ingest = dev_subcommands.add_parser("ingest", help="ingest local material")
    ingest.add_argument("inputs", nargs="+")
    ingest.add_argument("--wiki")
    ingest.add_argument(
        "--using",
        choices=tuple(kind.value for kind in HarnessKind),
    )
    ingest.add_argument("--title")
    ingest.add_argument("--guidance")
    ingest_mode = ingest.add_mutually_exclusive_group()
    ingest_mode.add_argument("--background", action="store_true")
    ingest_mode.add_argument("--foreground", action="store_true")
    ingest.add_argument("--json", action="store_true")

    garden = dev_subcommands.add_parser("garden", help="garden the local wiki")
    garden.add_argument("--wiki")
    garden.add_argument(
        "--using",
        choices=tuple(kind.value for kind in HarnessKind),
    )
    garden.add_argument("--title")
    garden.add_argument("--guidance")
    garden_mode = garden.add_mutually_exclusive_group()
    garden_mode.add_argument("--background", action="store_true")
    garden_mode.add_argument("--foreground", action="store_true")
    garden.add_argument("--json", action="store_true")
