from pathlib import Path

import pytest

from codealmanac.core.errors import ValidationFailed
from codealmanac.workflows.cloud_open.requests import OpenCloudTargetRequest
from codealmanac.workflows.cloud_open.service import CloudOpenWorkflow
from codealmanac.workflows.local_setup.models import LocalRepositoryState


def test_cloud_open_workflow_opens_wiki_url_for_current_github_checkout(
    tmp_path: Path,
) -> None:
    browser = FakeBrowser()
    workflow = CloudOpenWorkflow(
        FakeRepositoryProbe(local_repository_state(tmp_path / "repo")),
        browser,
    )

    result = workflow.open(
        OpenCloudTargetRequest(
            cwd=tmp_path / "repo",
            app_url="https://app.example.test/",
        )
    )

    assert result.url == "https://app.example.test/wiki/github/AlmanacCode/codealmanac"
    assert result.opened is True
    assert browser.opened == [result.url]


def test_cloud_open_workflow_builds_setup_and_repo_targets(tmp_path: Path) -> None:
    workflow = CloudOpenWorkflow(
        FakeRepositoryProbe(local_repository_state(tmp_path / "repo")),
        FakeBrowser(),
    )

    setup = workflow.open(
        OpenCloudTargetRequest(
            cwd=tmp_path / "repo",
            app_url="https://app.example.test",
            target="setup",
            no_browser=True,
        )
    )
    repo = workflow.open(
        OpenCloudTargetRequest(
            cwd=tmp_path / "repo",
            app_url="https://app.example.test",
            target="repo",
            no_browser=True,
        )
    )
    settings = workflow.open(
        OpenCloudTargetRequest(
            cwd=tmp_path / "repo",
            app_url="https://app.example.test",
            target="settings",
            no_browser=True,
        )
    )
    github_app = workflow.open(
        OpenCloudTargetRequest(
            cwd=tmp_path / "repo",
            app_url="https://app.example.test",
            target="github-app",
            no_browser=True,
        )
    )

    assert setup.url == (
        "https://app.example.test/setup/repo?"
        "provider=github&owner=AlmanacCode&repo=codealmanac"
    )
    assert repo.url == (
        "https://app.example.test/setup/repo?"
        "provider=github&owner=AlmanacCode&repo=codealmanac&target=activity"
    )
    assert settings.url == (
        "https://app.example.test/setup/repo?"
        "provider=github&owner=AlmanacCode&repo=codealmanac&target=settings"
    )
    assert github_app.url == (
        "https://app.example.test/setup/repo?"
        "provider=github&owner=AlmanacCode&repo=codealmanac&target=github-app"
    )
    assert setup.opened is False


def test_cloud_open_workflow_opens_github_direct_target(tmp_path: Path) -> None:
    workflow = CloudOpenWorkflow(
        FakeRepositoryProbe(local_repository_state(tmp_path / "repo")),
        FakeBrowser(),
    )

    result = workflow.open(
        OpenCloudTargetRequest(
            cwd=tmp_path / "repo",
            target="github",
            no_browser=True,
        )
    )

    assert result.url == "https://github.com/AlmanacCode/codealmanac"


def test_cloud_open_workflow_rejects_unavailable_checkout(tmp_path: Path) -> None:
    workflow = CloudOpenWorkflow(
        FakeRepositoryProbe(
            LocalRepositoryState(
                cwd=tmp_path / "repo",
                available=False,
                unavailable_reason="not a git repository",
            )
        ),
        FakeBrowser(),
    )

    with pytest.raises(ValidationFailed, match="not a git repository"):
        workflow.open(OpenCloudTargetRequest(cwd=tmp_path / "repo"))


class FakeBrowser:
    def __init__(self) -> None:
        self.opened: list[str] = []

    def open(self, url: str) -> bool:
        self.opened.append(url)
        return True


class FakeRepositoryProbe:
    def __init__(self, state: LocalRepositoryState) -> None:
        self.state = state

    def read(self, cwd: Path) -> LocalRepositoryState:
        return self.state


def local_repository_state(repo: Path) -> LocalRepositoryState:
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
