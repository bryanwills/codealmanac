from codealmanac.cloud.repositories.models import (
    CloudRepository,
    CloudRepositoryPage,
    CloudRepositoryTriggerPolicy,
)
from codealmanac.core.models import CodeAlmanacModel
from codealmanac.workflows.local_setup.models import LocalRepositoryState


class CloudRepoStatusResult(CodeAlmanacModel):
    checkout: LocalRepositoryState
    repository: CloudRepository | None = None
    triggers: tuple[CloudRepositoryTriggerPolicy, ...] = ()


class CloudRepoListResult(CodeAlmanacModel):
    repositories: CloudRepositoryPage


class CloudRepoTriggerPoliciesResult(CodeAlmanacModel):
    status: CloudRepoStatusResult
    triggers: tuple[CloudRepositoryTriggerPolicy, ...] = ()


class CloudRepoTriggerPolicyResult(CodeAlmanacModel):
    status: CloudRepoStatusResult
    trigger: CloudRepositoryTriggerPolicy
