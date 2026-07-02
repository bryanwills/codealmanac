from pathlib import Path

from codealmanac.core.errors import ValidationFailed
from codealmanac.services.control.models import ControlDeliveryMode
from codealmanac.services.control.requests import (
    SetBranchPolicyRequest,
    UpsertRepositoryRequest,
)
from codealmanac.services.control.service import ControlService
from codealmanac.services.local_hooks.requests import InstallLocalHooksRequest
from codealmanac.services.local_hooks.service import LocalHooksService
from codealmanac.workflows.local_setup.models import (
    LocalRepositoryState,
    LocalSetupResult,
)
from codealmanac.workflows.local_setup.ports import LocalRepositoryProbe
from codealmanac.workflows.local_setup.requests import RunLocalSetupRequest

LOCAL_SETUP_DELIVERY_MODES = frozenset(
    (ControlDeliveryMode.COMMIT, ControlDeliveryMode.WORKING_TREE)
)


class LocalSetupWorkflow:
    def __init__(
        self,
        control: ControlService,
        local_hooks: LocalHooksService,
        repository_probe: LocalRepositoryProbe,
    ):
        self.control = control
        self.local_hooks = local_hooks
        self.repository_probe = repository_probe

    def setup(self, request: RunLocalSetupRequest) -> LocalSetupResult:
        if request.delivery_mode not in LOCAL_SETUP_DELIVERY_MODES:
            raise ValidationFailed(
                f"unsupported local delivery mode: {request.delivery_mode.value}"
            )
        state = self.repository_probe.read(request.cwd)
        require_available_repository(state)
        branch_name = request.branch_name or require_text(
            state.branch_name,
            "current branch",
        )
        repository = self.control.upsert_repository(
            UpsertRepositoryRequest(
                provider=require_text(state.provider, "repository provider"),
                owner_login=require_text(state.owner_login, "repository owner"),
                name=require_text(state.name, "repository name"),
                full_name=require_text(state.full_name, "repository full name"),
                default_branch=state.default_branch,
                almanac_root=request.almanac_root,
                local_root_path=require_path(
                    state.repository_root,
                    "repository root",
                ),
            )
        )
        branch = self.control.set_branch_policy(
            SetBranchPolicyRequest(
                repository_id=repository.id,
                name=branch_name,
                trigger_enabled=True,
                delivery_mode=request.delivery_mode,
                last_seen_head_sha=state.head_sha
                if branch_name == state.branch_name
                else None,
            )
        )
        hooks = None
        if request.install_hooks:
            hooks = self.local_hooks.install(
                InstallLocalHooksRequest(
                    repo_root=require_path(
                        state.repository_root,
                        "repository root",
                    )
                )
            )
        return LocalSetupResult(repository=repository, branch=branch, hooks=hooks)


def require_available_repository(state: LocalRepositoryState) -> None:
    if state.available:
        return
    raise ValidationFailed(state.unavailable_reason or "local repository unavailable")


def require_text(value: str | None, name: str) -> str:
    if value is None:
        raise ValidationFailed(f"{name} is required")
    return value


def require_path(value: Path | None, name: str) -> Path:
    if value is None:
        raise ValidationFailed(f"{name} is required")
    return value
