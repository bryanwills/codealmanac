from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.runs.models import RunId


class WorkerWorkspacePaths(CodeAlmanacModel):
    run_id: RunId
    root_path: Path
    repo_path: Path
    sources_path: Path
    run_path: Path


class GitWorktreeCheckout(CodeAlmanacModel):
    repo_path: Path
    head_sha: str


class PreparedWorkerWorkspace(CodeAlmanacModel):
    paths: WorkerWorkspacePaths
    checkout: GitWorktreeCheckout
