from uuid import UUID

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.cloud_runs.models import CloudRun, CloudRunEvent, CloudRunPage
from codealmanac.workflows.cloud_repo.models import CloudRepoStatusResult


class CloudRunListResult(CodeAlmanacModel):
    status: CloudRepoStatusResult
    page: CloudRunPage


class CloudRunDetailResult(CodeAlmanacModel):
    run: CloudRun


class CloudRunLogResult(CodeAlmanacModel):
    run_id: UUID
    events: tuple[CloudRunEvent, ...]
