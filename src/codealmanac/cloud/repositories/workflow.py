from codealmanac.cloud.repositories.requests import (
    ListCloudRepositoriesRequest,
    ListCloudRepositoryTriggersRequest,
    ResolveCloudRepositoryRequest,
    UpsertCloudRepositoryTriggerRequest,
)
from codealmanac.cloud.repositories.service import CloudRepositoriesService
from codealmanac.cloud.repositories.workflow_models import (
    CloudRepoListResult,
    CloudRepoStatusResult,
    CloudRepoTriggerPoliciesResult,
    CloudRepoTriggerPolicyResult,
)
from codealmanac.cloud.repositories.workflow_requests import (
    ListCloudReposRequest,
    ListCloudRepoTriggersRequest,
    ReadCloudRepoStatusRequest,
    SetCloudRepoDeliveryRequest,
    UpdateCloudRepoTriggerRequest,
)
from codealmanac.core.errors import ValidationFailed
from codealmanac.local.setup.ports import LocalRepositoryProbe


class CloudRepoWorkflow:
    def __init__(
        self,
        cloud_repositories: CloudRepositoriesService,
        repository_probe: LocalRepositoryProbe,
    ):
        self.cloud_repositories = cloud_repositories
        self.repository_probe = repository_probe

    def list(self, request: ListCloudReposRequest) -> CloudRepoListResult:
        repositories = self.cloud_repositories.list(
            ListCloudRepositoriesRequest(
                api_url=request.api_url,
                limit=request.limit,
                cursor=request.cursor,
            )
        )
        return CloudRepoListResult(repositories=repositories)

    def status(self, request: ReadCloudRepoStatusRequest) -> CloudRepoStatusResult:
        checkout = self.repository_probe.read(request.cwd)
        if not checkout.available or checkout.full_name is None:
            return CloudRepoStatusResult(checkout=checkout)
        repository = self.cloud_repositories.resolve(
            ResolveCloudRepositoryRequest(
                api_url=request.api_url,
                full_name=checkout.full_name,
            )
        )
        triggers = self.cloud_repositories.list_triggers(
            ListCloudRepositoryTriggersRequest(
                api_url=request.api_url,
                repo_id=repository.repo_id,
            )
        )
        return CloudRepoStatusResult(
            checkout=checkout,
            repository=repository,
            triggers=triggers,
        )

    def list_triggers(
        self,
        request: ListCloudRepoTriggersRequest,
    ) -> CloudRepoTriggerPoliciesResult:
        status = self.status(
            ReadCloudRepoStatusRequest(cwd=request.cwd, api_url=request.api_url)
        )
        if status.repository is None:
            raise unavailable_checkout(status)
        return CloudRepoTriggerPoliciesResult(
            status=status,
            triggers=status.triggers,
        )

    def enable_trigger(
        self,
        request: UpdateCloudRepoTriggerRequest,
    ) -> CloudRepoTriggerPolicyResult:
        status = self.status(
            ReadCloudRepoStatusRequest(cwd=request.cwd, api_url=request.api_url)
        )
        if status.repository is None:
            raise unavailable_checkout(status)
        trigger = self.cloud_repositories.upsert_trigger(
            UpsertCloudRepositoryTriggerRequest(
                api_url=request.api_url,
                repo_id=status.repository.repo_id,
                branch=request.branch,
                enabled=True,
                delivery_mode=request.delivery_mode,
            )
        )
        return CloudRepoTriggerPolicyResult(status=status, trigger=trigger)

    def disable_trigger(
        self,
        request: UpdateCloudRepoTriggerRequest,
    ) -> CloudRepoTriggerPolicyResult:
        status = self.status(
            ReadCloudRepoStatusRequest(cwd=request.cwd, api_url=request.api_url)
        )
        if status.repository is None:
            raise unavailable_checkout(status)
        trigger = self.cloud_repositories.upsert_trigger(
            UpsertCloudRepositoryTriggerRequest(
                api_url=request.api_url,
                repo_id=status.repository.repo_id,
                branch=request.branch,
                enabled=False,
            )
        )
        return CloudRepoTriggerPolicyResult(status=status, trigger=trigger)

    def set_delivery(
        self,
        request: SetCloudRepoDeliveryRequest,
    ) -> CloudRepoTriggerPolicyResult:
        status = self.status(
            ReadCloudRepoStatusRequest(cwd=request.cwd, api_url=request.api_url)
        )
        if status.repository is None:
            raise unavailable_checkout(status)
        trigger = self.cloud_repositories.upsert_trigger(
            UpsertCloudRepositoryTriggerRequest(
                api_url=request.api_url,
                repo_id=status.repository.repo_id,
                branch=request.branch,
                delivery_mode=request.delivery_mode,
            )
        )
        return CloudRepoTriggerPolicyResult(status=status, trigger=trigger)


def unavailable_checkout(status: CloudRepoStatusResult) -> ValidationFailed:
    reason = status.checkout.unavailable_reason or "GitHub checkout unavailable"
    return ValidationFailed(reason)
