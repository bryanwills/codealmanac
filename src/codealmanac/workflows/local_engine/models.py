from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.control.models import ControlRunRecord
from codealmanac.services.engine_runs.models import EngineRunResult
from codealmanac.services.harnesses.models import HarnessRunResult


class LocalEngineRunResult(CodeAlmanacModel):
    executed: bool
    reason: str | None = None
    run: ControlRunRecord
    engine: EngineRunResult | None = None
    harness: HarnessRunResult | None = None
