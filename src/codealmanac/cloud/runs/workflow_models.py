from uuid import UUID

from codealmanac.cloud.repositories.workflow_models import CloudRepoStatusResult
from codealmanac.cloud.runs.models import CloudRun, CloudRunEvent, CloudRunPage
from codealmanac.core.models import CodeAlmanacModel


class CloudRunListResult(CodeAlmanacModel):
    status: CloudRepoStatusResult
    page: CloudRunPage


class CloudRunDetailResult(CodeAlmanacModel):
    run: CloudRun


class CloudRunLogResult(CodeAlmanacModel):
    run_id: UUID
    events: tuple[CloudRunEvent, ...]
