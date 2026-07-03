from typing import Protocol

from codealmanac.services.cloud_repositories.models import (
    CloudDeliveryMode,
    CloudRepository,
    CloudRepositoryPage,
    CloudRepositoryTriggerPolicy,
)


class CloudRepositoriesClient(Protocol):
    def list_repositories(
        self,
        *,
        api_url: str,
        cli_token: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> CloudRepositoryPage:
        pass

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
