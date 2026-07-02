from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.control.models import BranchRecord
from codealmanac.workflows.local_status.models import LocalStatusResult


class LocalTriggerPoliciesResult(CodeAlmanacModel):
    status: LocalStatusResult
    branches: tuple[BranchRecord, ...] = ()


class LocalTriggerPolicyResult(CodeAlmanacModel):
    status: LocalStatusResult
    branch: BranchRecord
