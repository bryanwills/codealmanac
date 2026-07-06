from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.harnesses.models import HarnessKind


class RunBuildRequest(CodeAlmanacModel):
    path: Path
    harness: HarnessKind
    name: str | None = None
    description: str = ""
    title: str | None = None
    guidance: str | None = None
    auto_commit: bool = True
