import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.dispatch.config import load_user_cli_config, resolve_harness
from codealmanac.cli.render.root import (
    render_init,
    render_init_json,
    render_run_started,
)
from codealmanac.workflows.build.requests import BuildRequest


def dispatch_init(args: argparse.Namespace, app: CodeAlmanac) -> int:
    cli_config = load_user_cli_config(app)
    request = BuildRequest(
        path=Path(args.path),
        harness=resolve_harness(args.using, cli_config),
        name=args.name,
        description=args.description,
        guidance=args.guidance,
        auto_commit=cli_config.auto_commit,
    )
    start = app.workflows.build.start(request)
    if not args.json:
        render_run_started(start.run, label="init")
    result = app.workflows.build.run_started(request, start)
    if args.json:
        render_init_json(result, app.local_state.database_path)
        return 0
    render_init(result, app.local_state.database_path)
    return 0
