import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.render.common import print_json_model
from codealmanac.services.control.models import ControlDeliveryMode
from codealmanac.services.workspaces.roots import DEFAULT_ALMANAC_ROOT
from codealmanac.workflows.local_setup.requests import RunLocalSetupRequest

LOCAL_COMMANDS = frozenset(("local",))


def is_local_command(command: str | None) -> bool:
    return command in LOCAL_COMMANDS


def dispatch_local(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.local_command == "setup":
        return dispatch_local_setup(args, app)
    raise AssertionError(f"unhandled local command: {args.local_command}")


def dispatch_local_setup(args: argparse.Namespace, app: CodeAlmanac) -> int:
    result = app.workflows.local_setup.setup(
        RunLocalSetupRequest(
            cwd=Path.cwd(),
            branch_name=args.branch,
            almanac_root=parse_almanac_root(args.root),
            delivery_mode=parse_delivery_mode(args.delivery),
            install_hooks=not args.skip_hooks,
        )
    )
    if args.json:
        print_json_model(result)
        return 0
    hooks_status = "installed" if result.hooks is not None else "skipped"
    print(
        "local setup: "
        f"{result.repository.full_name} "
        f"{result.branch.name} "
        f"{format_delivery_mode(result.branch.delivery_mode)}"
    )
    print(f"hooks: {hooks_status}")
    return 0


def parse_almanac_root(value: str | None) -> Path:
    if value is None:
        return DEFAULT_ALMANAC_ROOT
    return Path(value)


def parse_delivery_mode(value: str) -> ControlDeliveryMode:
    return ControlDeliveryMode(value.replace("-", "_"))


def format_delivery_mode(mode: ControlDeliveryMode) -> str:
    return mode.value.replace("_", "-")
