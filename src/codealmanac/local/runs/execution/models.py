from codealmanac.core.models import CodeAlmanacModel
from codealmanac.engine.harnesses.models import HarnessRunResult
from codealmanac.local.control.models import ControlRunRecord
from codealmanac.local.runs.artifacts.models import EngineRunResult


class LocalEngineRunResult(CodeAlmanacModel):
    executed: bool
    reason: str | None = None
    run: ControlRunRecord
    engine: EngineRunResult | None = None
    harness: HarnessRunResult | None = None
