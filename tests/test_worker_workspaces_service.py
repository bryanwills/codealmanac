import shutil
import subprocess
from pathlib import Path

import pytest

from codealmanac.app import create_app
from codealmanac.core.errors import ConflictError
from codealmanac.core.models import AppConfig
from codealmanac.core.paths import default_worker_workspaces_path
from codealmanac.services.worker_workspaces.models import GitWorktreeCheckout
from codealmanac.services.worker_workspaces.requests import (
    PrepareWorkerWorkspaceRequest,
    ReadWorkerWorkspaceRequest,
    RemoveWorkerWorkspaceRequest,
)


class FakeGitWorktreeManager:
    def __init__(self):
        self.add_calls: list[tuple[Path, Path, str]] = []
        self.remove_calls: list[tuple[Path, Path]] = []

    def add_detached(
        self,
        source_repo_path: Path,
        worktree_path: Path,
        commit_sha: str,
    ) -> GitWorktreeCheckout:
        self.add_calls.append((source_repo_path, worktree_path, commit_sha))
        worktree_path.mkdir(parents=True)
        return GitWorktreeCheckout(repo_path=worktree_path, head_sha=commit_sha)

    def remove(self, source_repo_path: Path, worktree_path: Path) -> None:
        self.remove_calls.append((source_repo_path, worktree_path))


def test_default_worker_workspaces_path_uses_codealmanac_home(
    isolated_home: Path,
):
    expected = isolated_home / ".codealmanac/workspaces"

    assert default_worker_workspaces_path() == expected
    assert AppConfig().worker_workspaces_path == expected


def test_worker_workspace_prepare_creates_layout_and_git_worktree(
    tmp_path: Path,
    isolated_home: Path,
):
    fake_git = FakeGitWorktreeManager()
    app = create_app(
        AppConfig(
            registry_path=isolated_home / ".codealmanac/registry.json",
            worker_workspaces_path=isolated_home / ".codealmanac/workspaces",
        ),
        git_worktree_manager=fake_git,
    )
    repo = tmp_path / "repo"

    prepared = app.worker_workspaces.prepare(
        PrepareWorkerWorkspaceRequest(
            run_id="run-1",
            repository_root_path=repo,
            expected_head_sha="abc123",
        )
    )

    assert prepared.paths.root_path == isolated_home / ".codealmanac/workspaces/run-1"
    assert prepared.paths.repo_path.is_dir()
    assert prepared.paths.sources_path.is_dir()
    assert prepared.paths.run_path.is_dir()
    assert prepared.checkout.head_sha == "abc123"
    assert fake_git.add_calls == [(repo, prepared.paths.repo_path, "abc123")]


def test_worker_workspace_prepare_rejects_existing_run_workspace(
    tmp_path: Path,
    isolated_home: Path,
):
    fake_git = FakeGitWorktreeManager()
    app = create_app(
        AppConfig(
            registry_path=isolated_home / ".codealmanac/registry.json",
            worker_workspaces_path=isolated_home / ".codealmanac/workspaces",
        ),
        git_worktree_manager=fake_git,
    )
    request = PrepareWorkerWorkspaceRequest(
        run_id="run-1",
        repository_root_path=tmp_path / "repo",
        expected_head_sha="abc123",
    )

    app.worker_workspaces.prepare(request)

    with pytest.raises(ConflictError):
        app.worker_workspaces.prepare(request)


def test_worker_workspace_remove_delegates_git_and_removes_tree(
    tmp_path: Path,
    isolated_home: Path,
):
    fake_git = FakeGitWorktreeManager()
    app = create_app(
        AppConfig(
            registry_path=isolated_home / ".codealmanac/registry.json",
            worker_workspaces_path=isolated_home / ".codealmanac/workspaces",
        ),
        git_worktree_manager=fake_git,
    )
    repo = tmp_path / "repo"
    prepared = app.worker_workspaces.prepare(
        PrepareWorkerWorkspaceRequest(
            run_id="run-1",
            repository_root_path=repo,
            expected_head_sha="abc123",
        )
    )

    app.worker_workspaces.remove(
        RemoveWorkerWorkspaceRequest(run_id="run-1", repository_root_path=repo)
    )

    assert fake_git.remove_calls == [(repo, prepared.paths.repo_path)]
    assert not prepared.paths.root_path.exists()


def test_worker_workspace_paths_returns_typed_layout(
    isolated_home: Path,
):
    app = create_app(
        AppConfig(
            registry_path=isolated_home / ".codealmanac/registry.json",
            worker_workspaces_path=isolated_home / ".codealmanac/workspaces",
        )
    )

    paths = app.worker_workspaces.paths(ReadWorkerWorkspaceRequest(run_id="run-1"))

    assert paths.root_path == isolated_home / ".codealmanac/workspaces/run-1"
    assert paths.repo_path == paths.root_path / "repo"
    assert paths.sources_path == paths.root_path / "sources"
    assert paths.run_path == paths.root_path / "run"


def test_git_detached_worktree_manager_creates_expected_head_worktree(
    tmp_path: Path,
    isolated_home: Path,
):
    if shutil.which("git") is None:
        pytest.skip("git is required for this integration test")
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init", "-q")
    run_git(repo, "config", "user.email", "test@example.com")
    run_git(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    run_git(repo, "add", "README.md")
    run_git(repo, "commit", "-m", "initial", "--quiet")
    head_sha = git_stdout(repo, "rev-parse", "HEAD")
    app = create_app(
        AppConfig(
            registry_path=isolated_home / ".codealmanac/registry.json",
            worker_workspaces_path=isolated_home / ".codealmanac/workspaces",
        )
    )

    prepared = app.worker_workspaces.prepare(
        PrepareWorkerWorkspaceRequest(
            run_id="run-real",
            repository_root_path=repo,
            expected_head_sha=head_sha,
        )
    )

    assert git_stdout(prepared.paths.repo_path, "rev-parse", "HEAD") == head_sha
    assert (prepared.paths.repo_path / "README.md").read_text(encoding="utf-8") == (
        "hello\n"
    )

    app.worker_workspaces.remove(
        RemoveWorkerWorkspaceRequest(run_id="run-real", repository_root_path=repo)
    )
    assert not prepared.paths.root_path.exists()


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ("git", *args),
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )


def git_stdout(repo: Path, *args: str) -> str:
    return subprocess.run(
        ("git", *args),
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
