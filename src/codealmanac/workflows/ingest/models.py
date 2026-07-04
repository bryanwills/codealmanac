from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.engine.harnesses.models import HarnessRunResult
from codealmanac.engine.lifecycle import LifecycleMutationReport
from codealmanac.engine.sources.models import SourceBrief, SourceRuntime
from codealmanac.runs.ledger.models import RunRecord
from codealmanac.wiki.index.models import IndexRefreshResult


class IngestPromptPayload(CodeAlmanacModel):
    workspace_name: str
    workspace_root: Path
    almanac_root: Path
    sources: tuple[SourceBrief, ...]
    source_runtime: tuple[SourceRuntime, ...]
    guidance: str | None = None


class IngestResult(CodeAlmanacModel):
    run: RunRecord
    sources: tuple[SourceBrief, ...]
    source_runtime: tuple[SourceRuntime, ...]
    harness: HarnessRunResult
    safety: LifecycleMutationReport
    index: IndexRefreshResult
