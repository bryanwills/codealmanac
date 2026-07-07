from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.manual import ManualDocument
from codealmanac.services.harnesses.models import HarnessRunResult
from codealmanac.services.index.models import (
    HealthReport,
    IndexRefreshResult,
    IndexSummary,
)
from codealmanac.services.runs.models import RunRecord
from codealmanac.workflows.operations.commit import OperationCommitPolicy


class GardenPromptPayload(CodeAlmanacModel):
    repository_name: str
    repository_root: Path
    almanac_root: Path
    wiki_source_root: Path
    topics_file: Path
    index: IndexSummary
    health: HealthReport
    manual_documents: tuple[ManualDocument, ...]
    source_control: OperationCommitPolicy
    guidance: str | None = None


class GardenResult(CodeAlmanacModel):
    run: RunRecord
    harness: HarnessRunResult
    index: IndexRefreshResult
    health_before: HealthReport
