from datetime import datetime

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.cloud_auth.models import CloudLoginResultStatus


class CloudLoginWorkflowResult(CodeAlmanacModel):
    api_url: str
    status: CloudLoginResultStatus
    github_user_id: int | None = None
    github_login: str | None = None
    verification_url: str | None = None
    user_code: str | None = None
    expires_at: datetime | None = None
