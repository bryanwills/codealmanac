from enum import StrEnum
from pathlib import Path

from pydantic import Field

from codealmanac.core.models import CodeAlmanacModel


class LocalGitHookName(StrEnum):
    POST_COMMIT = "post-commit"
    POST_MERGE = "post-merge"
    POST_REWRITE = "post-rewrite"


DEFAULT_LOCAL_TRIGGER_HOOKS = (
    LocalGitHookName.POST_COMMIT,
    LocalGitHookName.POST_MERGE,
    LocalGitHookName.POST_REWRITE,
)


class LocalGitHookChange(CodeAlmanacModel):
    hook: LocalGitHookName
    path: Path
    changed: bool
    installed: bool
    message: str = Field(min_length=1)


class LocalGitHooksResult(CodeAlmanacModel):
    repo_root: Path
    changes: tuple[LocalGitHookChange, ...]
