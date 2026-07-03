from pathlib import Path

from codealmanac.core.errors import ValidationFailed
from codealmanac.local.control.models import (
    BranchRecord,
    ControlDeliveryMode,
    RepositoryRecord,
)
from codealmanac.local.control.requests import (
    FindBranchByNameRequest,
    ListBranchesRequest,
    SetBranchPolicyRequest,
)
from codealmanac.local.control.service import ControlService
from codealmanac.local.policies.models import (
    LocalTriggerPoliciesResult,
    LocalTriggerPolicyResult,
)
from codealmanac.local.policies.requests import (
    ListLocalTriggerPoliciesRequest,
    SetLocalDeliveryPolicyRequest,
    UpdateLocalTriggerPolicyRequest,
)
from codealmanac.local.status.models import LocalStatusResult
from codealmanac.local.status.requests import ReadLocalStatusRequest
from codealmanac.local.status.service import LocalStatusWorkflow

LOCAL_POLICY_DELIVERY_MODES = frozenset(
    (ControlDeliveryMode.COMMIT, ControlDeliveryMode.WORKING_TREE)
)


class LocalPolicyWorkflow:
    def __init__(
        self,
        control: ControlService,
        local_status: LocalStatusWorkflow,
    ):
        self.control = control
        self.local_status = local_status

    def list_triggers(
        self,
        request: ListLocalTriggerPoliciesRequest,
    ) -> LocalTriggerPoliciesResult:
        status, repository = self.configured_repository(request.cwd)
        branches = self.control.list_branches(
            ListBranchesRequest(repository_id=repository.id)
        )
        return LocalTriggerPoliciesResult(status=status, branches=branches)

    def enable_trigger(
        self,
        request: UpdateLocalTriggerPolicyRequest,
    ) -> LocalTriggerPolicyResult:
        status, repository = self.configured_repository(request.cwd)
        existing = self.find_branch(repository, request.branch_name)
        delivery_mode = request.delivery_mode or existing_delivery(existing)
        validate_local_delivery_mode(delivery_mode)
        branch = self.control.set_branch_policy(
            SetBranchPolicyRequest(
                repository_id=repository.id,
                name=request.branch_name,
                trigger_enabled=True,
                delivery_mode=delivery_mode,
                last_seen_head_sha=current_head_for_branch(
                    status,
                    request.branch_name,
                ),
            )
        )
        return LocalTriggerPolicyResult(status=status, branch=branch)

    def disable_trigger(
        self,
        request: UpdateLocalTriggerPolicyRequest,
    ) -> LocalTriggerPolicyResult:
        status, repository = self.configured_repository(request.cwd)
        existing = self.find_branch(repository, request.branch_name)
        delivery_mode = request.delivery_mode or existing_delivery(existing)
        validate_local_delivery_mode(delivery_mode)
        branch = self.control.set_branch_policy(
            SetBranchPolicyRequest(
                repository_id=repository.id,
                name=request.branch_name,
                trigger_enabled=False,
                delivery_mode=delivery_mode,
            )
        )
        return LocalTriggerPolicyResult(status=status, branch=branch)

    def set_delivery(
        self,
        request: SetLocalDeliveryPolicyRequest,
    ) -> LocalTriggerPolicyResult:
        validate_local_delivery_mode(request.delivery_mode)
        status, repository = self.configured_repository(request.cwd)
        existing = self.find_branch(repository, request.branch_name)
        if existing is None:
            raise ValidationFailed(
                "branch policy not found; run "
                f"codealmanac local triggers enable {request.branch_name}"
            )
        branch = self.control.set_branch_policy(
            SetBranchPolicyRequest(
                repository_id=repository.id,
                name=existing.name,
                trigger_enabled=existing.trigger_enabled,
                delivery_mode=request.delivery_mode,
            )
        )
        return LocalTriggerPolicyResult(status=status, branch=branch)

    def configured_repository(
        self,
        cwd: Path,
    ) -> tuple[LocalStatusResult, RepositoryRecord]:
        status = self.local_status.status(ReadLocalStatusRequest(cwd=cwd))
        checkout = status.checkout
        if not checkout.available:
            raise ValidationFailed(
                checkout.unavailable_reason or "local checkout is unavailable"
            )
        if status.repository is None:
            raise ValidationFailed(
                "current checkout is not configured; run codealmanac local setup"
            )
        return status, status.repository

    def find_branch(
        self,
        repository: RepositoryRecord,
        branch_name: str,
    ) -> BranchRecord | None:
        return self.control.find_branch_by_name(
            FindBranchByNameRequest(
                repository_id=repository.id,
                name=branch_name,
            )
        )


def existing_delivery(branch: BranchRecord | None) -> ControlDeliveryMode:
    if branch is None:
        return ControlDeliveryMode.COMMIT
    return branch.delivery_mode


def validate_local_delivery_mode(mode: ControlDeliveryMode) -> None:
    if mode not in LOCAL_POLICY_DELIVERY_MODES:
        raise ValidationFailed(f"unsupported local delivery mode: {mode.value}")


def current_head_for_branch(
    status: LocalStatusResult,
    branch_name: str,
) -> str | None:
    checkout = status.checkout
    if checkout.branch_name != branch_name:
        return None
    return checkout.head_sha
