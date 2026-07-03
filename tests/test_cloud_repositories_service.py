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
from codealmanac.cloud.repositories.requests import (
    ListCloudRepositoriesRequest,
    ListCloudRepositoryTriggersRequest,
    ResolveCloudRepositoryRequest,
    UpsertCloudRepositoryTriggerRequest,
)
from codealmanac.cloud.repositories.service import CloudRepositoriesService


def test_cloud_repository_service_uses_stored_cli_token(tmp_path: Path) -> None:
    client = FakeCloudRepositoriesClient()
    service = CloudRepositoriesService(sign_in(tmp_path), client)

    page = service.list(
        ListCloudRepositoriesRequest(
            api_url="https://api.example.test",
            limit=5,
            cursor="1",
        )
    )
    repo = service.resolve(
        ResolveCloudRepositoryRequest(
            api_url="https://api.example.test",
            full_name="acme/api",
        )
    )
    triggers = service.list_triggers(
        ListCloudRepositoryTriggersRequest(
            api_url="https://api.example.test",
            repo_id=repo.repo_id,
        )
    )
    updated = service.upsert_trigger(
        UpsertCloudRepositoryTriggerRequest(
            api_url="https://api.example.test",
            repo_id=repo.repo_id,
            branch="release/1.4",
            enabled=False,
            delivery_mode="commit",
        )
    )

    assert page.items[0].full_name == "acme/api"
    assert repo.full_name == "acme/api"
    assert triggers[0].branch == "main"
    assert updated.delivery_mode == "commit"
    assert client.calls == [
        ("list-repos", "alm_secret", 5, "1"),
        ("resolve", "alm_secret", "acme/api"),
        ("list", "alm_secret", 1),
        ("upsert", "alm_secret", 1, "release/1.4", False, "commit"),
    ]


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
        self.calls: list[tuple] = []

    def list_repositories(
        self,
        *,
        api_url: str,
        cli_token: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> CloudRepositoryPage:
        self.calls.append(("list-repos", cli_token, limit, cursor))
        return CloudRepositoryPage(
            items=(
                CloudRepository(
                    repo_id=1,
                    account_id=10,
                    full_name="acme/api",
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
        self.calls.append(("resolve", cli_token, full_name))
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
        self.calls.append(("list", cli_token, repo_id))
        return (
            CloudRepositoryTriggerPolicy(
                repo_id=repo_id,
                branch="main",
                enabled=True,
                delivery_mode="pr",
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
        self.calls.append(
            ("upsert", cli_token, repo_id, branch, enabled, delivery_mode)
        )
        return CloudRepositoryTriggerPolicy(
            repo_id=repo_id,
            branch=branch,
            enabled=enabled if enabled is not None else True,
            delivery_mode=delivery_mode if delivery_mode is not None else "commit",
        )
