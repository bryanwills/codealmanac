from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.index.models import IndexRefreshResult
from codealmanac.services.workspaces.models import Workspace


class BuildResult(CodeAlmanacModel):
    workspace: Workspace
    index: IndexRefreshResult
