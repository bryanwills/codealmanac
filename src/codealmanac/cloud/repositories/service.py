from codealmanac.cloud.auth.requests import CloudStatusRequest
from codealmanac.cloud.auth.service import CloudAuthService
from codealmanac.cloud.repositories.models import (
    CloudRepository,
    CloudRepositoryPage,
    CloudRepositoryTriggerPolicy,
)
from codealmanac.cloud.repositories.ports import CloudRepositoriesClient
from codealmanac.cloud.repositories.requests import (
    ListCloudRepositoriesRequest,
    ListCloudRepositoryTriggersRequest,
    ResolveCloudRepositoryRequest,
    UpsertCloudRepositoryTriggerRequest,
)


class CloudRepositoriesService:
    def __init__(self, auth: CloudAuthService, client: CloudRepositoriesClient):
        self.auth = auth
        self.client = client

    def list(self, request: ListCloudRepositoriesRequest) -> CloudRepositoryPage:
        state = self.auth.require_state(CloudStatusRequest(api_url=request.api_url))
        return self.client.list_repositories(
            api_url=request.api_url,
            cli_token=state.token,
            limit=request.limit,
            cursor=request.cursor,
        )

    def resolve(self, request: ResolveCloudRepositoryRequest) -> CloudRepository:
        state = self.auth.require_state(CloudStatusRequest(api_url=request.api_url))
        return self.client.resolve_repository(
            api_url=request.api_url,
            cli_token=state.token,
            full_name=request.full_name,
        )

    def list_triggers(
        self,
        request: ListCloudRepositoryTriggersRequest,
    ) -> tuple[CloudRepositoryTriggerPolicy, ...]:
        state = self.auth.require_state(CloudStatusRequest(api_url=request.api_url))
        return self.client.list_repository_triggers(
            api_url=request.api_url,
            cli_token=state.token,
            repo_id=request.repo_id,
        )

    def upsert_trigger(
        self,
        request: UpsertCloudRepositoryTriggerRequest,
    ) -> CloudRepositoryTriggerPolicy:
        state = self.auth.require_state(CloudStatusRequest(api_url=request.api_url))
        return self.client.upsert_repository_trigger(
            api_url=request.api_url,
            cli_token=state.token,
            repo_id=request.repo_id,
            branch=request.branch,
            enabled=request.enabled,
            delivery_mode=request.delivery_mode,
        )
