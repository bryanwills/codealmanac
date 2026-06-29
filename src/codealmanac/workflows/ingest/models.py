from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.harnesses.models import HarnessRunResult
from codealmanac.services.index.models import IndexRefreshResult
from codealmanac.services.runs.models import RunRecord
from codealmanac.services.sources.models import SourceBrief


class IngestPromptPayload(CodeAlmanacModel):
    workspace_name: str
    workspace_root: Path
    almanac_root: Path
    sources: tuple[SourceBrief, ...]
    guidance: str | None = None


class IngestResult(CodeAlmanacModel):
    run: RunRecord
    sources: tuple[SourceBrief, ...]
    harness: HarnessRunResult
    index: IndexRefreshResult
