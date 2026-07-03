import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.render.cloud_open import render_cloud_open
from codealmanac.cli.render.repo import (
    render_cloud_repo_list,
    render_cloud_repo_status,
    render_cloud_repo_trigger_policies,
    render_cloud_repo_trigger_policy,
)
from codealmanac.services.cloud_repositories.models import CloudDeliveryMode
from codealmanac.workflows.cloud_open.models import CloudOpenTarget
from codealmanac.workflows.cloud_open.requests import OpenCloudTargetRequest
from codealmanac.workflows.cloud_repo.requests import (
    ListCloudReposRequest,
    ListCloudRepoTriggersRequest,
    ReadCloudRepoStatusRequest,
    SetCloudRepoDeliveryRequest,
    UpdateCloudRepoTriggerRequest,
)

REPO_COMMANDS = frozenset(("repo",))


def is_repo_command(command: str | None) -> bool:
    return command in REPO_COMMANDS


def dispatch_repo(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.repo_command == "list":
        result = app.workflows.cloud_repo.list(
            ListCloudReposRequest(
                api_url=args.api_url,
                limit=args.limit,
                cursor=args.cursor,
            )
        )
        render_cloud_repo_list(result, json_output=args.json)
        return 0
    if args.repo_command == "setup":
        result = app.workflows.cloud_open.open(
            OpenCloudTargetRequest(
                cwd=Path.cwd(),
                app_url=args.app_url,
                target="setup",
                no_browser=args.no_browser,
            )
        )
        render_cloud_open(result, json_output=args.json)
        return 0
    if args.repo_command == "open":
        result = app.workflows.cloud_open.open(
            OpenCloudTargetRequest(
                cwd=Path.cwd(),
                app_url=args.app_url,
                target=parse_cloud_open_target(args.target),
                no_browser=args.no_browser,
            )
        )
        render_cloud_open(result, json_output=args.json)
        return 0
    if args.repo_command == "status":
        result = app.workflows.cloud_repo.status(
            ReadCloudRepoStatusRequest(cwd=Path.cwd(), api_url=args.api_url)
        )
        render_cloud_repo_status(result, json_output=args.json)
        return 0 if result.repository is not None else 1
    if args.repo_command == "triggers":
        return dispatch_repo_triggers(args, app)
    if args.repo_command == "delivery":
        return dispatch_repo_delivery(args, app)
    raise AssertionError(f"unhandled repo command: {args.repo_command}")


def dispatch_repo_triggers(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.triggers_command == "list":
        result = app.workflows.cloud_repo.list_triggers(
            ListCloudRepoTriggersRequest(cwd=Path.cwd(), api_url=args.api_url)
        )
        render_cloud_repo_trigger_policies(result, json_output=args.json)
        return 0
    if args.triggers_command == "enable":
        result = app.workflows.cloud_repo.enable_trigger(
            UpdateCloudRepoTriggerRequest(
                cwd=Path.cwd(),
                api_url=args.api_url,
                branch=args.branch,
                delivery_mode=parse_cloud_delivery_mode(args.delivery),
            )
        )
        render_cloud_repo_trigger_policy(result, json_output=args.json)
        return 0
    if args.triggers_command == "disable":
        result = app.workflows.cloud_repo.disable_trigger(
            UpdateCloudRepoTriggerRequest(
                cwd=Path.cwd(),
                api_url=args.api_url,
                branch=args.branch,
            )
        )
        render_cloud_repo_trigger_policy(result, json_output=args.json)
        return 0
    raise AssertionError(f"unhandled repo triggers command: {args.triggers_command}")


def dispatch_repo_delivery(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.delivery_command == "set":
        result = app.workflows.cloud_repo.set_delivery(
            SetCloudRepoDeliveryRequest(
                cwd=Path.cwd(),
                api_url=args.api_url,
                branch=args.branch,
                delivery_mode=parse_cloud_delivery_mode(args.mode),
            )
        )
        render_cloud_repo_trigger_policy(result, json_output=args.json)
        return 0
    raise AssertionError(f"unhandled repo delivery command: {args.delivery_command}")


def parse_cloud_delivery_mode(value: str) -> CloudDeliveryMode:
    if value not in ("commit", "pr"):
        raise AssertionError(f"unhandled cloud delivery mode: {value}")
    return value


def parse_cloud_open_target(value: str) -> CloudOpenTarget:
    if value == "activity":
        return "repo"
    if value in ("settings", "github", "github-app"):
        return value
    raise AssertionError(f"unhandled cloud open target: {value}")
