from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from codealmanac.cloud.auth.models import CloudIdentity, CloudLoginSession
from codealmanac.cloud.auth.requests import SaveCloudTokenRequest
from codealmanac.cloud.auth.service import CloudAuthService
from codealmanac.cloud.auth.store import CloudAuthStore
from codealmanac.cloud.repositories.models import (
    CloudRepository,
    CloudRepositoryPage,
    CloudRepositoryTriggerPolicy,
)
from codealmanac.cloud.repositories.service import CloudRepositoriesService
from codealmanac.cloud.repositories.workflow import CloudRepoWorkflow
from codealmanac.cloud.repositories.workflow_requests import (
    ListCloudReposRequest,
    ListCloudRepoTriggersRequest,
    ReadCloudRepoStatusRequest,
    SetCloudRepoDeliveryRequest,
    UpdateCloudRepoTriggerRequest,
)
from codealmanac.workflows.local_setup.models import LocalRepositoryState


def test_cloud_repo_workflow_resolves_current_checkout_and_updates_triggers(
    tmp_path: Path,
) -> None:
    client = FakeCloudRepositoriesClient()
    workflow = CloudRepoWorkflow(
        CloudRepositoriesService(sign_in(tmp_path), client),
        FakeRepositoryProbe(local_repository_state(tmp_path / "repo")),
    )

    status = workflow.status(
        ReadCloudRepoStatusRequest(
            cwd=tmp_path / "repo",
            api_url="https://api.example.test",
        )
    )
    listed = workflow.list_triggers(
        ListCloudRepoTriggersRequest(
            cwd=tmp_path / "repo",
            api_url="https://api.example.test",
        )
    )
    enabled = workflow.enable_trigger(
        UpdateCloudRepoTriggerRequest(
            cwd=tmp_path / "repo",
            api_url="https://api.example.test",
            branch="dev",
            delivery_mode="pr",
        )
    )
    disabled = workflow.disable_trigger(
        UpdateCloudRepoTriggerRequest(
            cwd=tmp_path / "repo",
            api_url="https://api.example.test",
            branch="dev",
        )
    )
    delivery = workflow.set_delivery(
        SetCloudRepoDeliveryRequest(
            cwd=tmp_path / "repo",
            api_url="https://api.example.test",
            branch="dev",
            delivery_mode="commit",
        )
    )

    assert status.repository is not None
    assert status.repository.full_name == "AlmanacCode/codealmanac"
    assert listed.triggers[0].branch == "main"
    assert enabled.trigger.enabled is True
    assert enabled.trigger.delivery_mode == "pr"
    assert disabled.trigger.enabled is False
    assert delivery.trigger.delivery_mode == "commit"
    assert client.upserts == [
        ("dev", True, "pr"),
        ("dev", False, None),
        ("dev", None, "commit"),
    ]


class FakeRepositoryProbe:
    def __init__(self, state: LocalRepositoryState) -> None:
        self.state = state
        self.reads: list[Path] = []

    def read(self, cwd: Path) -> LocalRepositoryState:
        self.reads.append(cwd)
        return self.state


def test_cloud_repo_list_is_not_checkout_scoped(tmp_path: Path) -> None:
    client = FakeCloudRepositoriesClient()
    probe = FakeRepositoryProbe(local_repository_state(tmp_path / "repo"))
    workflow = CloudRepoWorkflow(
        CloudRepositoriesService(sign_in(tmp_path), client),
        probe,
    )

    result = workflow.list(
        ListCloudReposRequest(
            api_url="https://api.example.test",
            limit=5,
            cursor="1",
        )
    )

    assert [repository.full_name for repository in result.repositories.items] == [
        "AlmanacCode/codealmanac"
    ]
    assert result.repositories.next_cursor is None
    assert client.repo_lists == [(5, "1")]
    assert probe.reads == []


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


def sign_in(tmp_path: Path) -> CloudAuthService:
    service = CloudAuthService(
        CloudAuthStore(tmp_path / "auth.json"),
        FakeCloudAuthClient(),
    )
    service.save_token(
        SaveCloudTokenRequest(
            api_url="https://api.example.test",
            token="alm_secret",
            logged_in_at=datetime(2026, 7, 2, 12, tzinfo=UTC),
        )
    )
    return service


class FakeCloudAuthClient:
    def start_login(self, *, api_url: str) -> CloudLoginSession:
        raise NotImplementedError

    def poll_login(self, *, api_url: str, session_id: UUID) -> CloudLoginSession:
        raise NotImplementedError

    def me(self, *, api_url: str, token: str) -> CloudIdentity:
        assert token == "alm_secret"
        return CloudIdentity(
            api_url=api_url,
            github_user_id=10,
            github_login="rohans0509",
        )

    def logout(self, *, api_url: str, token: str) -> CloudIdentity:
        return self.me(api_url=api_url, token=token)


class FakeCloudRepositoriesClient:
    def __init__(self) -> None:
        self.repo_lists: list[tuple[int | None, str | None]] = []
        self.upserts: list[tuple[str, bool | None, str | None]] = []

    def list_repositories(
        self,
        *,
        api_url: str,
        cli_token: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> CloudRepositoryPage:
        assert cli_token == "alm_secret"
        self.repo_lists.append((limit, cursor))
        return CloudRepositoryPage(
            items=(
                CloudRepository(
                    repo_id=1,
                    account_id=10,
                    full_name="AlmanacCode/codealmanac",
                    default_branch="main",
                ),
            ),
            next_cursor=None,
        )

    def resolve_repository(
        self,
        *,
        api_url: str,
        cli_token: str,
        full_name: str,
    ) -> CloudRepository:
        assert cli_token == "alm_secret"
        return CloudRepository(
            repo_id=1,
            account_id=10,
            full_name=full_name,
            default_branch="main",
        )

    def list_repository_triggers(
        self,
        *,
        api_url: str,
        cli_token: str,
        repo_id: int,
    ) -> tuple[CloudRepositoryTriggerPolicy, ...]:
        assert cli_token == "alm_secret"
        return (
            CloudRepositoryTriggerPolicy(
                repo_id=repo_id,
                branch="main",
                enabled=True,
                delivery_mode="commit",
            ),
        )

    def upsert_repository_trigger(
        self,
        *,
        api_url: str,
        cli_token: str,
        repo_id: int,
        branch: str,
        enabled: bool | None = None,
        delivery_mode=None,
    ) -> CloudRepositoryTriggerPolicy:
        assert cli_token == "alm_secret"
        self.upserts.append((branch, enabled, delivery_mode))
        return CloudRepositoryTriggerPolicy(
            repo_id=repo_id,
            branch=branch,
            enabled=enabled if enabled is not None else True,
            delivery_mode=delivery_mode if delivery_mode is not None else "commit",
        )
