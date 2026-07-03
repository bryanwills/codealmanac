from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.engine.harnesses.models import HarnessRunResult
from codealmanac.engine.lifecycle import (
    LifecycleMutationPreflight,
    LifecycleMutationReport,
)
from codealmanac.services.runs.models import RunId, RunRecord
from codealmanac.wiki.index.models import IndexRefreshResult
from codealmanac.wiki.workspaces.models import Workspace


class PageRunContext(CodeAlmanacModel):
    cwd: Path
    run_id: RunId
    workspace: Workspace
    wiki: str | None = None
    preflight: LifecycleMutationPreflight | None = None


class PageRunResult(CodeAlmanacModel):
    run: RunRecord
    harness: HarnessRunResult
    safety: LifecycleMutationReport
    index: IndexRefreshResult
