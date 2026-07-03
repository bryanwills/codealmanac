from codealmanac.core.models import CodeAlmanacModel
from codealmanac.engine.harnesses.models import HarnessRunResult
from codealmanac.services.control.models import ControlRunRecord
from codealmanac.services.engine_runs.models import EngineRunResult


class LocalEngineRunResult(CodeAlmanacModel):
    executed: bool
    reason: str | None = None
    run: ControlRunRecord
    engine: EngineRunResult | None = None
    harness: HarnessRunResult | None = None
