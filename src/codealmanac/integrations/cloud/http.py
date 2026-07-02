from datetime import datetime
from typing import Any
from uuid import UUID

import httpx

from codealmanac.core.errors import ExecutionFailed
from codealmanac.services.cloud_auth.models import CloudIdentity, CloudLoginSession


class HttpCloudAuthClient:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def start_login(self, *, api_url: str) -> CloudLoginSession:
        data = self._request("POST", f"{api_url}/v1/auth/cli/start")
        return login_session(data)

    def poll_login(self, *, api_url: str, session_id: UUID) -> CloudLoginSession:
        data = self._request(
            "POST",
            f"{api_url}/v1/auth/cli/sessions/{session_id}/poll",
        )
        return login_session(data)

    def me(self, *, api_url: str, token: str) -> CloudIdentity:
        data = self._request(
            "GET",
            f"{api_url}/v1/me",
            token=token,
        )
        return identity(api_url, data)

    def logout(self, *, api_url: str, token: str) -> CloudIdentity:
        data = self._request(
            "POST",
            f"{api_url}/v1/auth/logout",
            token=token,
        )
        return identity(api_url, data)

    def _request(
        self,
        method: str,
        url: str,
        *,
        token: str | None = None,
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {token}"} if token is not None else None
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, url, headers=headers)
        except httpx.HTTPError as error:
            raise ExecutionFailed(f"cloud request failed: {error}") from error
        if response.status_code >= 400:
            message = response.text.strip() or response.reason_phrase
            raise ExecutionFailed(
                f"cloud request failed ({response.status_code}): {message}"
            )
        try:
            payload = response.json()
        except ValueError as error:
            raise ExecutionFailed("cloud returned invalid JSON") from error
        if not isinstance(payload, dict):
            raise ExecutionFailed("cloud returned invalid JSON")
        return payload


def login_session(data: dict[str, Any]) -> CloudLoginSession:
    return CloudLoginSession(
        session_id=UUID(str(data["sessionId"])),
        user_code=str(data["userCode"]),
        verification_url=str(data["verificationUrl"]),
        expires_at=datetime.fromisoformat(
            str(data["expiresAt"]).replace("Z", "+00:00")
        ),
        status=data["status"],
        token=data.get("token"),
    )


def identity(api_url: str, data: dict[str, Any]) -> CloudIdentity:
    return CloudIdentity(
        api_url=api_url,
        github_user_id=int(data["githubUserId"]),
        github_login=str(data["githubLogin"]),
    )
