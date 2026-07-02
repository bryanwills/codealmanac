from pathlib import Path

import pytest

from codealmanac.app import create_app
from codealmanac.core.errors import ValidationFailed
from codealmanac.core.models import AppConfig
from codealmanac.services.control.models import ControlDeliveryMode
from codealmanac.services.control.requests import (
    SetBranchPolicyRequest,
    UpsertRepositoryRequest,
)
from codealmanac.workflows.local_policy.requests import (
    ListLocalTriggerPoliciesRequest,
    SetLocalDeliveryPolicyRequest,
    UpdateLocalTriggerPolicyRequest,
)
from codealmanac.workflows.local_setup.models import LocalRepositoryState


class FakeLocalRepositoryProbe:
    def __init__(self, state: LocalRepositoryState):
        self.state = state
        self.requests: list[Path] = []

    def read(self, cwd: Path) -> LocalRepositoryState:
        self.requests.append(cwd)
        return self.state


def test_local_policy_lists_configured_branch_policies(
    tmp_path: Path,
    isolated_home: Path,
):
    app, repo, repository, _probe = local_policy_app(tmp_path, isolated_home)
    app.control.set_branch_policy(
        SetBranchPolicyRequest(repository_id=repository.id, name="main")
    )
    app.control.set_branch_policy(
        SetBranchPolicyRequest(
            repository_id=repository.id,
            name="dev",
            delivery_mode=ControlDeliveryMode.WORKING_TREE,
        )
    )

    result = app.workflows.local_policy.list_triggers(
        ListLocalTriggerPoliciesRequest(cwd=repo / "src")
    )

    assert tuple(branch.name for branch in result.branches) == ("dev", "main")
    assert result.branches[0].delivery_mode is ControlDeliveryMode.WORKING_TREE


def test_local_policy_enable_preserves_existing_delivery_mode(
    tmp_path: Path,
    isolated_home: Path,
):
    app, repo, repository, _probe = local_policy_app(tmp_path, isolated_home)
    app.control.set_branch_policy(
        SetBranchPolicyRequest(
            repository_id=repository.id,
            name="dev",
            trigger_enabled=False,
            delivery_mode=ControlDeliveryMode.WORKING_TREE,
        )
    )

    result = app.workflows.local_policy.enable_trigger(
        UpdateLocalTriggerPolicyRequest(cwd=repo, branch_name="dev")
    )

    assert result.branch.trigger_enabled is True
    assert result.branch.delivery_mode is ControlDeliveryMode.WORKING_TREE
    assert result.branch.last_seen_head_sha == "head-1"


def test_local_policy_disable_preserves_existing_delivery_mode(
    tmp_path: Path,
    isolated_home: Path,
):
    app, repo, repository, _probe = local_policy_app(tmp_path, isolated_home)
    app.control.set_branch_policy(
        SetBranchPolicyRequest(
            repository_id=repository.id,
            name="dev",
            trigger_enabled=True,
            delivery_mode=ControlDeliveryMode.WORKING_TREE,
        )
    )

    result = app.workflows.local_policy.disable_trigger(
        UpdateLocalTriggerPolicyRequest(cwd=repo, branch_name="dev")
    )

    assert result.branch.trigger_enabled is False
    assert result.branch.delivery_mode is ControlDeliveryMode.WORKING_TREE


def test_local_policy_delivery_set_preserves_trigger_state(
    tmp_path: Path,
    isolated_home: Path,
):
    app, repo, repository, _probe = local_policy_app(tmp_path, isolated_home)
    app.control.set_branch_policy(
        SetBranchPolicyRequest(
            repository_id=repository.id,
            name="dev",
            trigger_enabled=False,
            delivery_mode=ControlDeliveryMode.COMMIT,
        )
    )

    result = app.workflows.local_policy.set_delivery(
        SetLocalDeliveryPolicyRequest(
            cwd=repo,
            branch_name="dev",
            delivery_mode=ControlDeliveryMode.WORKING_TREE,
        )
    )

    assert result.branch.trigger_enabled is False
    assert result.branch.delivery_mode is ControlDeliveryMode.WORKING_TREE


def test_local_policy_delivery_set_requires_existing_branch(
    tmp_path: Path,
    isolated_home: Path,
):
    app, repo, _repository, _probe = local_policy_app(tmp_path, isolated_home)

    with pytest.raises(ValidationFailed, match="branch policy not found"):
        app.workflows.local_policy.set_delivery(
            SetLocalDeliveryPolicyRequest(
                cwd=repo,
                branch_name="main",
                delivery_mode=ControlDeliveryMode.WORKING_TREE,
            )
        )


def test_local_policy_requires_configured_repository(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(control_db_path=isolated_home / ".codealmanac/control.sqlite"),
        local_repository_probe=FakeLocalRepositoryProbe(available_state(repo)),
    )

    with pytest.raises(ValidationFailed, match="current checkout is not configured"):
        app.workflows.local_policy.list_triggers(
            ListLocalTriggerPoliciesRequest(cwd=repo)
        )


def local_policy_app(tmp_path: Path, isolated_home: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    probe = FakeLocalRepositoryProbe(available_state(repo))
    app = create_app(
        AppConfig(control_db_path=isolated_home / ".codealmanac/control.sqlite"),
        local_repository_probe=probe,
    )
    repository = app.control.upsert_repository(
        UpsertRepositoryRequest(
            provider="github",
            owner_login="AlmanacCode",
            name="codealmanac",
            full_name="AlmanacCode/codealmanac",
            almanac_root=Path("almanac"),
            local_root_path=repo,
        )
    )
    return app, repo, repository, probe


def available_state(repo: Path) -> LocalRepositoryState:
    return LocalRepositoryState(
        cwd=repo,
        available=True,
        repository_root=repo,
        branch_name="dev",
        head_sha="head-1",
        provider="github",
        owner_login="AlmanacCode",
        name="codealmanac",
        full_name="AlmanacCode/codealmanac",
        default_branch="main",
    )
