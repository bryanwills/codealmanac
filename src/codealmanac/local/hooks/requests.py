from pathlib import Path

from pydantic import Field

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.local.hooks.models import (
    DEFAULT_LOCAL_TRIGGER_HOOKS,
    LocalGitHookName,
)


class InstallLocalHooksRequest(CodeAlmanacModel):
    repo_root: Path
    hooks: tuple[LocalGitHookName, ...] = Field(
        default=DEFAULT_LOCAL_TRIGGER_HOOKS,
    )


class UninstallLocalHooksRequest(CodeAlmanacModel):
    repo_root: Path
    hooks: tuple[LocalGitHookName, ...] = Field(
        default=DEFAULT_LOCAL_TRIGGER_HOOKS,
    )
