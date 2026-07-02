import shutil
import subprocess
from pathlib import Path

import pytest

from codealmanac.integrations.workspaces.git.repository import (
    GitLocalRepositoryProbe,
    parse_github_remote,
)


def test_parse_github_remote_accepts_https_and_ssh_forms():
    assert parse_github_remote("https://github.com/AlmanacCode/codealmanac.git")
    assert parse_github_remote("git@github.com:AlmanacCode/codealmanac.git")
    assert parse_github_remote("ssh://git@github.com/AlmanacCode/codealmanac.git")
    assert parse_github_remote("https://gitlab.com/AlmanacCode/codealmanac") is None


def test_git_local_repository_probe_reads_current_checkout(tmp_path: Path):
    if shutil.which("git") is None:
        pytest.skip("git is required for this integration test")
    repo = create_repo(tmp_path / "repo")
    nested = repo / "src/package"
    nested.mkdir(parents=True)

    state = GitLocalRepositoryProbe().read(nested)

    assert state.available is True
    assert state.repository_root == repo
    assert state.branch_name == "dev"
    assert state.head_sha == git_stdout(repo, "rev-parse", "HEAD")
    assert state.provider == "github"
    assert state.owner_login == "AlmanacCode"
    assert state.name == "codealmanac"
    assert state.full_name == "AlmanacCode/codealmanac"


def test_git_local_repository_probe_reports_non_git_directory(tmp_path: Path):
    state = GitLocalRepositoryProbe().read(tmp_path)

    assert state.available is False
    assert state.unavailable_reason is not None


def create_repo(repo: Path) -> Path:
    repo.mkdir()
    run_git(repo, "init", "-q")
    run_git(repo, "config", "user.email", "test@example.com")
    run_git(repo, "config", "user.name", "Test User")
    run_git(repo, "checkout", "-b", "dev")
    run_git(
        repo,
        "remote",
        "add",
        "origin",
        "git@github.com:AlmanacCode/codealmanac.git",
    )
    (repo / "README.md").write_text("repo\n", encoding="utf-8")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-m", "initial", "--quiet")
    return repo


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
