from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from codealmanac.core.errors import ValidationFailed
from codealmanac.services.cloud_auth.models import CloudIdentity, CloudLoginSession
from codealmanac.services.cloud_auth.requests import (
    CloudLogoutRequest,
    CloudStatusRequest,
    SaveCloudTokenRequest,
)
from codealmanac.services.cloud_auth.service import CloudAuthService
from codealmanac.services.cloud_auth.store import CloudAuthStore


def test_cloud_auth_store_saves_cli_token_state_mode_0600(tmp_path: Path) -> None:
    store = CloudAuthStore(tmp_path / "auth.json")
    service = CloudAuthService(store, FakeCloudAuthClient())

    identity = service.save_token(
        SaveCloudTokenRequest(
            api_url="https://api.example.test",
            token="alm_secret",
            logged_in_at=datetime(2026, 7, 2, 12, tzinfo=UTC),
        )
    )
    loaded = store.load()

    assert identity.github_login == "rohans0509"
    assert loaded is not None
    assert loaded.token == "alm_secret"
    assert oct((tmp_path / "auth.json").stat().st_mode & 0o777) == "0o600"


def test_cloud_auth_status_validates_remote_identity(tmp_path: Path) -> None:
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

    status = service.status(CloudStatusRequest(api_url="https://api.example.test"))

    assert status.authenticated is True
    assert status.github_login == "rohans0509"


def test_cloud_auth_logout_removes_local_token_state(tmp_path: Path) -> None:
    store = CloudAuthStore(tmp_path / "auth.json")
    service = CloudAuthService(store, FakeCloudAuthClient())
    service.save_token(
        SaveCloudTokenRequest(
            api_url="https://api.example.test",
            token="alm_secret",
            logged_in_at=datetime(2026, 7, 2, 12, tzinfo=UTC),
        )
    )

    result = service.logout(CloudLogoutRequest(api_url="https://api.example.test"))

    assert result.signed_out is True
    assert result.github_login == "rohans0509"
    assert store.load() is None


def test_cloud_auth_store_rejects_malformed_auth_json(tmp_path: Path) -> None:
    path = tmp_path / "auth.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(ValidationFailed):
        CloudAuthStore(path).load()


class FakeCloudAuthClient:
    def start_login(self, *, api_url: str) -> CloudLoginSession:
        return login_session(uuid4(), status="pending")

    def poll_login(self, *, api_url: str, session_id: UUID) -> CloudLoginSession:
        return login_session(session_id, status="complete", token="alm_secret")

    def me(self, *, api_url: str, token: str) -> CloudIdentity:
        assert token == "alm_secret"
        return CloudIdentity(
            api_url=api_url,
            github_user_id=10,
            github_login="rohans0509",
        )

    def logout(self, *, api_url: str, token: str) -> CloudIdentity:
        return self.me(api_url=api_url, token=token)


def login_session(
    session_id: UUID,
    *,
    status: str,
    token: str | None = None,
) -> CloudLoginSession:
    return CloudLoginSession(
        session_id=session_id,
        user_code="ABCD2345",
        verification_url=f"https://app.example.test/cli-login?session={session_id}",
        expires_at=datetime(2026, 7, 2, 12, 10, tzinfo=UTC),
        status=status,  # type: ignore[arg-type]
        token=token,
    )
