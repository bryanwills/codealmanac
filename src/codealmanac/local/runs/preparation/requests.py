from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text


class PrepareNextLocalRunRequest(CodeAlmanacModel):
    repository_id: str | None = None
    branch_id: str | None = None
    kind: str = "update"

    @field_validator("repository_id", "branch_id")
    @classmethod
    def require_optional_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "local run preparation id")

    @field_validator("kind")
    @classmethod
    def require_kind(cls, value: str) -> str:
        return required_text(value, "local run preparation kind")
