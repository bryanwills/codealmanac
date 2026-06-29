import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from codealmanac import __version__
from codealmanac.app import create_app
from codealmanac.core.errors import CodeAlmanacError
from codealmanac.services.workspaces.requests import InitializeWorkspaceRequest


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return dispatch(args)
    except (CodeAlmanacError, ValidationError) as error:
        print(f"codealmanac: {error}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codealmanac",
        description="Maintain a local .almanac wiki for a codebase.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    init = subcommands.add_parser("init", help="initialize a local .almanac wiki")
    init.add_argument("path", nargs="?", default=".")
    init.add_argument("--name")
    init.add_argument("--description", default="")

    subcommands.add_parser("list", help="list registered local wikis")
    return parser


def dispatch(args: argparse.Namespace) -> int:
    app = create_app()
    if args.command == "init":
        workspace = app.build.initialize(
            InitializeWorkspaceRequest(
                path=Path(args.path),
                name=args.name,
                description=args.description,
            )
        )
        print(workspace.name)
        print(
            f"initialized {workspace.almanac_path} "
            f"(registry: {app.workspaces.store.path})",
            file=sys.stderr,
        )
        return 0
    if args.command == "list":
        for workspace in app.workspaces.list():
            print(f"{workspace.name}\t{workspace.root_path}")
        return 0
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
