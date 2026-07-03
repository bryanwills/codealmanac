from typing import Protocol

from codealmanac.cloud.auth.login_requests import RunCloudLoginRequest
from codealmanac.cloud.auth.models import CloudLoginSession
from codealmanac.core.models import CodeAlmanacModel


class BrowserOpener(Protocol):
    def open(self, url: str) -> bool:
        pass


class CloudLoginStartDecision(CodeAlmanacModel):
    open_browser: bool = False


class CloudLoginInteraction(Protocol):
    def started(
        self,
        session: CloudLoginSession,
        request: RunCloudLoginRequest,
    ) -> CloudLoginStartDecision:
        pass
