from codealmanac.core.models import CodeAlmanacModel
from codealmanac.local.control.models import ControlRunRecord
from codealmanac.local.delivery.execution.models import LocalDeliveryResult
from codealmanac.local.runs.execution.models import LocalEngineRunResult
from codealmanac.local.runs.preparation.models import LocalRunPreparationResult


class LocalWorkerRunResult(CodeAlmanacModel):
    processed: bool
    reason: str | None = None
    run: ControlRunRecord | None = None
    preparation: LocalRunPreparationResult | None = None
    engine: LocalEngineRunResult | None = None
    delivery: LocalDeliveryResult | None = None
