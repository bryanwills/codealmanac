from typing import Literal

from pydantic import Field

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.local.setup.models import LocalRepositoryState

CloudOpenTarget = Literal[
    "wiki",
    "repo",
    "setup",
    "settings",
    "github",
    "github-app",
]


class CloudOpenResult(CodeAlmanacModel):
    target: CloudOpenTarget
    url: str = Field(min_length=1)
    opened: bool
    checkout: LocalRepositoryState
