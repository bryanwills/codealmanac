from codealmanac.services.cloud_auth.requests import CloudStatusRequest
from codealmanac.services.cloud_auth.service import CloudAuthService
from codealmanac.services.cloud_repositories.models import (
    CloudRepository,
    CloudRepositoryTriggerPolicy,
)
from codealmanac.services.cloud_repositories.ports import CloudRepositoriesClient
from codealmanac.services.cloud_repositories.requests import (
    ListCloudRepositoryTriggersRequest,
    ResolveCloudRepositoryRequest,
    UpsertCloudRepositoryTriggerRequest,
)


class CloudRepositoriesService:
    def __init__(self, auth: CloudAuthService, client: CloudRepositoriesClient):
        self.auth = auth
        self.client = client

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
