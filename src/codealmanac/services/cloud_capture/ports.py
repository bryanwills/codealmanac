from pathlib import Path
from typing import Protocol

from codealmanac.services.cloud_capture.models import (
    CaptureArtifact,
    CaptureArtifactUpload,
    CaptureCloudStatus,
    CaptureCredentialIssue,
    CaptureHookChange,
    CaptureHookStatus,
    CaptureProvider,
    CaptureRepositoryState,
    CaptureTranscriptUpload,
    CaptureTurnUploadResult,
)


class CloudCaptureClient(Protocol):
    def issue_capture_credential(
        self,
        *,
        api_url: str,
        cli_token: str,
        name: str,
    ) -> CaptureCredentialIssue:
        pass

    def capture_status(self, *, api_url: str, cli_token: str) -> CaptureCloudStatus:
        pass

    def revoke_capture_credential(
        self,
        *,
        api_url: str,
        cli_token: str,
        capture_token: str,
    ) -> bool:
        pass

    def upload_capture_artifact(
        self,
        *,
        api_url: str,
        capture_token: str,
        artifact: CaptureArtifactUpload,
    ) -> CaptureArtifact:
        pass

    def upload_capture_turn(
        self,
        *,
        api_url: str,
        capture_token: str,
        turn: CaptureTranscriptUpload,
    ) -> CaptureTurnUploadResult:
        pass


class CaptureRepositoryProbe(Protocol):
    def read(self, cwd: Path) -> CaptureRepositoryState:
        pass


class CaptureTranscriptParser(Protocol):
    def artifact(
        self,
        *,
        provider: CaptureProvider,
        payload: dict[str, object],
    ) -> CaptureArtifactUpload | None:
        pass

    def normalize(
        self,
        *,
        provider: CaptureProvider,
        payload: dict[str, object],
        artifact: CaptureArtifact,
        repository: CaptureRepositoryState,
    ) -> CaptureTranscriptUpload | None:
        pass


class CaptureHookManager(Protocol):
    def install(self, provider: CaptureProvider) -> CaptureHookChange:
        pass

    def uninstall(self, provider: CaptureProvider) -> CaptureHookChange:
        pass

    def status(self, provider: CaptureProvider) -> CaptureHookStatus:
        pass
