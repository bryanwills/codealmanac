from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.engine.harnesses.models import HarnessRunResult
from codealmanac.engine.lifecycle import LifecycleMutationReport
from codealmanac.services.runs.models import RunRecord
from codealmanac.wiki.index.models import (
    HealthReport,
    IndexRefreshResult,
    IndexSummary,
)


class GardenPromptPayload(CodeAlmanacModel):
    workspace_name: str
    workspace_root: Path
    almanac_root: Path
    pages_root: Path
    topics_file: Path
    index: IndexSummary
    health: HealthReport
    guidance: str | None = None


class GardenResult(CodeAlmanacModel):
    run: RunRecord
    harness: HarnessRunResult
    safety: LifecycleMutationReport
    index: IndexRefreshResult
    health_before: HealthReport
