from pathlib import Path

import pytest

from codealmanac.app import create_app
from codealmanac.core.errors import ValidationFailed
from codealmanac.core.models import AppConfig
from codealmanac.local.control.models import ControlDeliveryMode
from codealmanac.local.hooks.models import (
    LocalGitHookChange,
    LocalGitHookName,
)
from codealmanac.local.setup.models import LocalRepositoryState
from codealmanac.local.setup.requests import RunLocalSetupRequest


class FakeLocalRepositoryProbe:
    def __init__(self, state: LocalRepositoryState):
        self.state = state
        self.requests: list[Path] = []

    def read(self, cwd: Path) -> LocalRepositoryState:
        self.requests.append(cwd)
        return self.state


class FakeLocalGitHookManager:
    def __init__(self):
        self.installs: list[tuple[Path, LocalGitHookName]] = []

    def install(
        self,
        repo_root: Path,
        hook: LocalGitHookName,
    ) -> LocalGitHookChange:
        self.installs.append((repo_root, hook))
        return LocalGitHookChange(
            hook=hook,
            path=repo_root / ".git/hooks" / hook.value,
            changed=True,
            installed=True,
            message="installed",
        )

    def uninstall(
        self,
        repo_root: Path,
        hook: LocalGitHookName,
    ) -> LocalGitHookChange:
        raise AssertionError("local setup should not uninstall hooks")


def test_local_setup_registers_checkout_branch_and_installs_hooks(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    hooks = FakeLocalGitHookManager()
    probe = FakeLocalRepositoryProbe(available_state(repo))
    app = create_app(
        AppConfig(
            registry_path=isolated_home / ".codealmanac/registry.json",
            control_db_path=isolated_home / ".codealmanac/control.sqlite",
        ),
        local_git_hook_manager=hooks,
        local_repository_probe=probe,
    )

    result = app.workflows.local_setup.setup(RunLocalSetupRequest(cwd=repo / "src"))

    assert result.repository.full_name == "AlmanacCode/codealmanac"
    assert result.repository.local_root_path == repo
    assert result.branch.name == "dev"
    assert result.branch.trigger_enabled is True
    assert result.branch.delivery_mode is ControlDeliveryMode.COMMIT
    assert result.branch.last_seen_head_sha == "head-1"
    assert result.hooks is not None
    assert probe.requests == [repo / "src"]
    assert tuple(hook for _root, hook in hooks.installs) == (
        LocalGitHookName.POST_COMMIT,
        LocalGitHookName.POST_MERGE,
        LocalGitHookName.POST_REWRITE,
    )


def test_local_setup_can_skip_hooks_and_use_working_tree_delivery(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    hooks = FakeLocalGitHookManager()
    app = create_app(
        AppConfig(control_db_path=isolated_home / ".codealmanac/control.sqlite"),
        local_git_hook_manager=hooks,
        local_repository_probe=FakeLocalRepositoryProbe(available_state(repo)),
    )

    result = app.workflows.local_setup.setup(
        RunLocalSetupRequest(
            cwd=repo,
            delivery_mode=ControlDeliveryMode.WORKING_TREE,
            install_hooks=False,
        )
    )

    assert result.branch.delivery_mode is ControlDeliveryMode.WORKING_TREE
    assert result.hooks is None
    assert hooks.installs == []


def test_local_setup_rejects_unavailable_git_checkout(
    tmp_path: Path,
    isolated_home: Path,
):
    probe = FakeLocalRepositoryProbe(
        LocalRepositoryState(
            cwd=tmp_path,
            available=False,
            unavailable_reason="not inside a Git checkout",
        )
    )
    app = create_app(
        AppConfig(control_db_path=isolated_home / ".codealmanac/control.sqlite"),
        local_repository_probe=probe,
    )

    with pytest.raises(ValidationFailed, match="not inside a Git checkout"):
        app.workflows.local_setup.setup(RunLocalSetupRequest(cwd=tmp_path))


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
