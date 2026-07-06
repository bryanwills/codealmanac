import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.render.root import render_build, render_init
from codealmanac.services.workspaces.requests import InitializeWorkspaceRequest


def dispatch_init(args: argparse.Namespace, app: CodeAlmanac) -> int:
    result = app.workflows.build.build(build_request(args))
    render_init(result.workspace, result.index, app.workspaces.store.path)
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
