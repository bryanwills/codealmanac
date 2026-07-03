from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.engine.harnesses.models import HarnessKind


class RunLocalUpdateRequest(CodeAlmanacModel):
    cwd: Path
    harness: HarnessKind = HarnessKind.CODEX
