import sys

from codealmanac.cli.render.common import print_json_model
from codealmanac.workflows.cloud_repo.models import (
    CloudRepoListResult,
    CloudRepoStatusResult,
    CloudRepoTriggerPoliciesResult,
    CloudRepoTriggerPolicyResult,
)


def render_cloud_repo_list(
    result: CloudRepoListResult,
    *,
    json_output: bool,
) -> None:
    if json_output:
        print_json_model(result)
        return
    repositories = result.repositories.items
    if len(repositories) == 0:
        print("# 0 cloud repositories", file=sys.stderr)
        return
    for repository in repositories:
        print(f"{repository.full_name}\t{repository.repo_id}\t{repository.account_id}")
    if result.repositories.next_cursor is not None:
        print(f"next_cursor: {result.repositories.next_cursor}", file=sys.stderr)


def render_cloud_repo_status(
    result: CloudRepoStatusResult,
    *,
    json_output: bool,
) -> None:
    if json_output:
        print_json_model(result)
        return
    checkout = result.checkout
    if not checkout.available:
        print("checkout: unavailable")
        if checkout.unavailable_reason is not None:
            print(f"reason: {checkout.unavailable_reason}")
        return
    print(f"checkout: {checkout.full_name} {checkout.branch_name} {checkout.head_sha}")
    if result.repository is None:
        print("cloud repository: not connected")
        return
    print(f"cloud repository: {result.repository.full_name}")
    print(f"repo_id: {result.repository.repo_id}")
    print(f"account_id: {result.repository.account_id}")
    print(f"triggers: {len(result.triggers)}")


def render_cloud_repo_trigger_policies(
    result: CloudRepoTriggerPoliciesResult,
    *,
    json_output: bool,
) -> None:
    if json_output:
        print_json_model(result)
        return
    if len(result.triggers) == 0:
        print("# 0 cloud triggers", file=sys.stderr)
        return
    for trigger in result.triggers:
        print(trigger_row(trigger.branch, trigger.enabled, trigger.delivery_mode))


def render_cloud_repo_trigger_policy(
    result: CloudRepoTriggerPolicyResult,
    *,
    json_output: bool,
) -> None:
    if json_output:
        print_json_model(result)
        return
    trigger = result.trigger
    print(f"branch: {trigger.branch}")
    print(f"triggers: {'enabled' if trigger.enabled else 'disabled'}")
    print(f"delivery: {trigger.delivery_mode}")


def trigger_row(branch: str, enabled: bool, delivery_mode: str) -> str:
    trigger = "enabled" if enabled else "disabled"
    return f"{branch}\t{trigger}\t{delivery_mode}"
