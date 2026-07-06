from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.manual import ManualDocument
from codealmanac.services.harnesses.models import HarnessRunResult
from codealmanac.services.index.models import IndexRefreshResult
from codealmanac.services.runs.models import RunRecord
from codealmanac.services.workspaces.models import Workspace
from codealmanac.workflows.lifecycle import LifecycleMutationReport
from codealmanac.workflows.lifecycle_commit import LifecycleCommitPolicy


class BuildPromptPayload(CodeAlmanacModel):
    workspace_name: str
    workspace_root: Path
    almanac_root: Path
    wiki_source_root: Path
    topics_file: Path
    manual_documents: tuple[ManualDocument, ...]
    source_control: LifecycleCommitPolicy
    guidance: str | None = None


class BuildResult(CodeAlmanacModel):
    workspace: Workspace
    index: IndexRefreshResult
    run: RunRecord | None = None
    harness: HarnessRunResult | None = None
    safety: LifecycleMutationReport | None = None
