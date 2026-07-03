from codealmanac.core.models import CodeAlmanacModel
from codealmanac.engine.harnesses.models import HarnessRunResult
from codealmanac.engine.runs.models import EngineRunResult
from codealmanac.local.control.models import ControlRunRecord


class LocalEngineRunResult(CodeAlmanacModel):
    executed: bool
    reason: str | None = None
    run: ControlRunRecord
    engine: EngineRunResult | None = None
    harness: HarnessRunResult | None = None
