from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.harnesses.models import HarnessRunResult
from codealmanac.services.index.models import (
    HealthReport,
    IndexRefreshResult,
    IndexSummary,
)
from codealmanac.services.runs.models import RunRecord
from codealmanac.workflows.lifecycle import LifecycleMutationReport
from codealmanac.workflows.lifecycle_commit import LifecycleCommitPolicy


class GardenPromptPayload(CodeAlmanacModel):
    workspace_name: str
    workspace_root: Path
    almanac_root: Path
    wiki_source_root: Path
    topics_file: Path
    index: IndexSummary
    health: HealthReport
    source_control: LifecycleCommitPolicy
    guidance: str | None = None


class GardenResult(CodeAlmanacModel):
    run: RunRecord
    harness: HarnessRunResult
    safety: LifecycleMutationReport
    index: IndexRefreshResult
    health_before: HealthReport
