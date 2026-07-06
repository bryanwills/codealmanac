import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.dispatch.config import (
    load_cli_config,
    resolve_harness,
    resolve_pending_timeout,
    resolve_quiet,
)
from codealmanac.cli.render.root import render_sync_status
from codealmanac.core.errors import ValidationFailed
from codealmanac.services.sources.models import TranscriptApp
from codealmanac.workflows.sync.models import SyncExecution
from codealmanac.workflows.sync.requests import (
    DEFAULT_SYNC_MAX_FAILED_ATTEMPTS,
    RunSyncRequest,
    RunSyncStatusRequest,
)


def dispatch_sync(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.sync_command == "status":
        return dispatch_sync_status(args, app)
    cli_config = load_cli_config(app, args.wiki)
    result = app.workflows.sync.run(
        RunSyncRequest(
            cwd=Path.cwd(),
            wiki=args.wiki,
            apps=parse_sync_apps(args.source_apps),
            quiet=resolve_quiet(args.quiet, cli_config),
            pending_timeout=resolve_pending_timeout(args.pending_timeout),
            max_failed_attempts=sync_max_failed_attempts(args),
            ignore_transcripts_before=cli_config.sync.ignore_transcripts_before,
            harness=resolve_harness(args.using, cli_config),
            execution=sync_execution(args),
            claim_owner=args.claim_owner,
            auto_commit=cli_config.auto_commit,
        )
    )
    render_sync_status(result, json_output=args.json)
    return 0


def dispatch_sync_status(args: argparse.Namespace, app: CodeAlmanac) -> int:
    cli_config = load_cli_config(app, args.wiki)
    result = app.workflows.sync.status(
        RunSyncStatusRequest(
            cwd=Path.cwd(),
            wiki=args.wiki,
            apps=parse_sync_apps(args.source_apps),
            quiet=resolve_quiet(args.quiet, cli_config),
            pending_timeout=resolve_pending_timeout(args.pending_timeout),
            max_failed_attempts=sync_max_failed_attempts(args),
            ignore_transcripts_before=cli_config.sync.ignore_transcripts_before,
        )
    )
    render_sync_status(result, json_output=args.json)
    return 0


def sync_max_failed_attempts(args: argparse.Namespace) -> int:
    if args.max_failed_attempts is not None:
        return args.max_failed_attempts
    return DEFAULT_SYNC_MAX_FAILED_ATTEMPTS


def sync_execution(args: argparse.Namespace) -> SyncExecution:
    if args.background:
        return SyncExecution.BACKGROUND
    return SyncExecution.FOREGROUND


def parse_sync_apps(value: str | None) -> tuple[TranscriptApp, ...]:
    if value is None or value.strip() == "":
        return (TranscriptApp.CLAUDE, TranscriptApp.CODEX)
    apps: list[TranscriptApp] = []
    for raw in value.split(","):
        item = raw.strip()
        try:
            app = TranscriptApp(item)
        except ValueError as error:
            raise ValidationFailed(
                f'invalid --from "{value}" (expected claude,codex)'
            ) from error
        if app not in apps:
            apps.append(app)
    if len(apps) == 0:
        raise ValidationFailed("at least one sync source is required")
    return tuple(apps)
