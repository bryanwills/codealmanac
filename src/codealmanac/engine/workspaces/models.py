from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.engine.run_ids import EngineRunId


class EngineWorkspacePaths(CodeAlmanacModel):
    run_id: EngineRunId
    root_path: Path
    repo_path: Path
    sources_path: Path
    run_path: Path


class GitWorktreeCheckout(CodeAlmanacModel):
    repo_path: Path
    head_sha: str


class PreparedEngineWorkspace(CodeAlmanacModel):
    paths: EngineWorkspacePaths
    checkout: GitWorktreeCheckout
