from typing import Protocol
from uuid import UUID

from codealmanac.services.cloud_auth.models import CloudIdentity, CloudLoginSession


class CloudAuthClient(Protocol):
    def start_login(self, *, api_url: str) -> CloudLoginSession:
        pass

    def poll_login(self, *, api_url: str, session_id: UUID) -> CloudLoginSession:
        pass

    def me(self, *, api_url: str, token: str) -> CloudIdentity:
        pass

    def logout(self, *, api_url: str, token: str) -> CloudIdentity:
        pass
