from codealmanac.cloud.auth.models import CloudStatus
from codealmanac.cloud.capture.models import CaptureStatus
from codealmanac.cloud.repositories.workflow_models import CloudRepoStatusResult
from codealmanac.core.models import CodeAlmanacModel


class CloudStatusOverview(CodeAlmanacModel):
    auth: CloudStatus
    repo: CloudRepoStatusResult | None = None
    capture: CaptureStatus
