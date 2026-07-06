import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.dispatch.config import load_user_cli_config, resolve_harness
from codealmanac.cli.render.root import render_build, render_init
from codealmanac.services.workspaces.requests import InitializeWorkspaceRequest
from codealmanac.workflows.build.requests import RunBuildRequest


def dispatch_init(args: argparse.Namespace, app: CodeAlmanac) -> int:
    cli_config = load_user_cli_config(app)
    result = app.workflows.build.run(
        RunBuildRequest(
            path=Path(args.path),
            harness=resolve_harness(args.using, cli_config),
            name=args.name,
            description=args.description,
            guidance=args.guidance,
            auto_commit=cli_config.auto_commit,
        )
    )
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
