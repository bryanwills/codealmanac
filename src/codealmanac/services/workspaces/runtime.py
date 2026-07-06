from pathlib import Path

from codealmanac.services.workspaces.models import Workspace


class WorkspaceRuntimePaths:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir

    def repo_dir(self, workspace: Workspace) -> Path:
        return self.state_dir / "repos" / workspace.workspace_id
