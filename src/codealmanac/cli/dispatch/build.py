import argparse
import sys
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.render.root import render_build
from codealmanac.services.workspaces.requests import InitializeWorkspaceRequest


def dispatch_init(args: argparse.Namespace, app: CodeAlmanac) -> int:
    workspace = app.workflows.build.initialize(build_request(args))
    print(workspace.name)
    print(
        f"initialized {workspace.almanac_path} "
        f"(registry: {app.workspaces.store.path})",
        file=sys.stderr,
    )
    return 0


def dispatch_build(args: argparse.Namespace, app: CodeAlmanac) -> int:
    result = app.workflows.build.build(build_request(args))
    render_build(result.workspace.name, result.index)
    return 0


def build_request(args: argparse.Namespace) -> InitializeWorkspaceRequest:
    return InitializeWorkspaceRequest(
        path=Path(args.path),
        name=args.name,
        description=args.description,
    )
