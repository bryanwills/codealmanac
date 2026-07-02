from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.control.models import ControlRunRecord
from codealmanac.workflows.local_delivery.models import LocalDeliveryResult
from codealmanac.workflows.local_engine.models import LocalEngineRunResult
from codealmanac.workflows.local_runs.models import LocalRunPreparationResult


class LocalWorkerRunResult(CodeAlmanacModel):
    processed: bool
    reason: str | None = None
    run: ControlRunRecord | None = None
    preparation: LocalRunPreparationResult | None = None
    engine: LocalEngineRunResult | None = None
    delivery: LocalDeliveryResult | None = None
