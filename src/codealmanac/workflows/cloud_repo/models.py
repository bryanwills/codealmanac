from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.cloud_repositories.models import (
    CloudRepository,
    CloudRepositoryTriggerPolicy,
)
from codealmanac.workflows.local_setup.models import LocalRepositoryState


class CloudRepoStatusResult(CodeAlmanacModel):
    checkout: LocalRepositoryState
    repository: CloudRepository | None = None
    triggers: tuple[CloudRepositoryTriggerPolicy, ...] = ()


class CloudRepoTriggerPoliciesResult(CodeAlmanacModel):
    status: CloudRepoStatusResult
    triggers: tuple[CloudRepositoryTriggerPolicy, ...] = ()


class CloudRepoTriggerPolicyResult(CodeAlmanacModel):
    status: CloudRepoStatusResult
    trigger: CloudRepositoryTriggerPolicy
