from typing import Protocol

from codealmanac.services.cloud_repositories.models import (
    CloudDeliveryMode,
    CloudRepository,
    CloudRepositoryTriggerPolicy,
)


class CloudRepositoriesClient(Protocol):
    def resolve_repository(
        self,
        *,
        api_url: str,
        cli_token: str,
        full_name: str,
    ) -> CloudRepository:
        pass

    def list_repository_triggers(
        self,
        *,
        api_url: str,
        cli_token: str,
        repo_id: int,
    ) -> tuple[CloudRepositoryTriggerPolicy, ...]:
        pass

    def upsert_repository_trigger(
        self,
        *,
        api_url: str,
        cli_token: str,
        repo_id: int,
        branch: str,
        enabled: bool | None = None,
        delivery_mode: CloudDeliveryMode | None = None,
    ) -> CloudRepositoryTriggerPolicy:
        pass
