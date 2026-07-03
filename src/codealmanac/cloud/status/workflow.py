from codealmanac.cloud.auth.requests import CloudStatusRequest
from codealmanac.cloud.auth.service import CloudAuthService
from codealmanac.cloud.capture.requests import CaptureStatusRequest
from codealmanac.cloud.capture.service import CloudCaptureService
from codealmanac.cloud.repositories.workflow import CloudRepoWorkflow
from codealmanac.cloud.repositories.workflow_requests import ReadCloudRepoStatusRequest
from codealmanac.cloud.status.models import CloudStatusOverview
from codealmanac.cloud.status.requests import ReadCloudStatusRequest


class CloudStatusWorkflow:
    def __init__(
        self,
        auth: CloudAuthService,
        repo: CloudRepoWorkflow,
        capture: CloudCaptureService,
    ):
        self.auth = auth
        self.repo = repo
        self.capture = capture

    def status(self, request: ReadCloudStatusRequest) -> CloudStatusOverview:
        auth = self.auth.status(
            CloudStatusRequest(api_url=request.api_url, validate_remote=True)
        )
        repo = None
        if auth.authenticated:
            repo = self.repo.status(
                ReadCloudRepoStatusRequest(
                    cwd=request.cwd,
                    api_url=request.api_url,
                )
            )
        capture = self.capture.status(
            CaptureStatusRequest(
                api_url=request.api_url,
                check_cloud=request.check_capture_cloud and auth.authenticated,
            )
        )
        return CloudStatusOverview(auth=auth, repo=repo, capture=capture)
