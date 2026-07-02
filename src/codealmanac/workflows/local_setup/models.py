from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.control.models import BranchRecord, RepositoryRecord
from codealmanac.services.local_hooks.models import LocalGitHooksResult


class LocalRepositoryState(CodeAlmanacModel):
    cwd: Path
    available: bool
    repository_root: Path | None = None
    branch_name: str | None = None
    head_sha: str | None = None
    provider: str | None = None
    owner_login: str | None = None
    name: str | None = None
    full_name: str | None = None
    default_branch: str | None = None
    unavailable_reason: str | None = None

    @field_validator(
        "branch_name",
        "head_sha",
        "provider",
        "owner_login",
        "name",
        "full_name",
        "default_branch",
        "unavailable_reason",
    )
    @classmethod
    def require_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "local repository state text")


class LocalSetupResult(CodeAlmanacModel):
    repository: RepositoryRecord
    branch: BranchRecord
    hooks: LocalGitHooksResult | None = None
