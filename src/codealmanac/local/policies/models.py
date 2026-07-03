from codealmanac.core.models import CodeAlmanacModel
from codealmanac.local.control.models import BranchRecord
from codealmanac.local.status.models import LocalStatusResult


class LocalTriggerPoliciesResult(CodeAlmanacModel):
    status: LocalStatusResult
    branches: tuple[BranchRecord, ...] = ()


class LocalTriggerPolicyResult(CodeAlmanacModel):
    status: LocalStatusResult
    branch: BranchRecord
