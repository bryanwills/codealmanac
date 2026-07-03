from codealmanac.cloud.auth.requests import CloudStatusRequest
from codealmanac.cloud.auth.service import CloudAuthService
from codealmanac.cloud.runs.models import CloudRun, CloudRunEvent, CloudRunPage
from codealmanac.cloud.runs.ports import CloudRunsClient
from codealmanac.cloud.runs.requests import (
    CancelCloudRunRequest,
    ListCloudRunEventsRequest,
    ListCloudRunsForRepoRequest,
    ReadCloudRunRequest,
    RetryCloudRunRequest,
    StartCloudRunForRepoRequest,
)


class CloudRunsService:
    def __init__(self, auth: CloudAuthService, client: CloudRunsClient):
        self.auth = auth
        self.client = client

    def list_for_repo(self, request: ListCloudRunsForRepoRequest) -> CloudRunPage:
        state = self.auth.require_state(CloudStatusRequest(api_url=request.api_url))
        return self.client.list_repository_runs(
            api_url=request.api_url,
            cli_token=state.token,
            repo_id=request.repo_id,
            limit=request.limit,
            cursor=request.cursor,
        )

    def start_for_repo(self, request: StartCloudRunForRepoRequest) -> CloudRun:
        state = self.auth.require_state(CloudStatusRequest(api_url=request.api_url))
        return self.client.start_repository_run(
            api_url=request.api_url,
            cli_token=state.token,
            repo_id=request.repo_id,
            branch=request.branch,
        )

    def read(self, request: ReadCloudRunRequest) -> CloudRun:
        state = self.auth.require_state(CloudStatusRequest(api_url=request.api_url))
        return self.client.read_run(
            api_url=request.api_url,
            cli_token=state.token,
            run_id=request.run_id,
        )

    def cancel(self, request: CancelCloudRunRequest) -> CloudRun:
        state = self.auth.require_state(CloudStatusRequest(api_url=request.api_url))
        return self.client.cancel_run(
            api_url=request.api_url,
            cli_token=state.token,
            run_id=request.run_id,
        )

    def retry(self, request: RetryCloudRunRequest) -> CloudRun:
        state = self.auth.require_state(CloudStatusRequest(api_url=request.api_url))
        return self.client.retry_run(
            api_url=request.api_url,
            cli_token=state.token,
            run_id=request.run_id,
        )

    def list_events(
        self,
        request: ListCloudRunEventsRequest,
    ) -> tuple[CloudRunEvent, ...]:
        state = self.auth.require_state(CloudStatusRequest(api_url=request.api_url))
        return self.client.list_run_events(
            api_url=request.api_url,
            cli_token=state.token,
            run_id=request.run_id,
        )
