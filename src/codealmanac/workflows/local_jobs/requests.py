from pydantic import Field, field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.control.models import ControlRunStatus


class ListLocalJobsRequest(CodeAlmanacModel):
    repository_id: str | None = None
    branch_id: str | None = None
    statuses: tuple[ControlRunStatus, ...] = Field(default_factory=tuple)
    limit: int = 20

    @field_validator("repository_id", "branch_id")
    @classmethod
    def require_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "local job list filter")

    @field_validator("limit")
    @classmethod
    def require_valid_limit(cls, value: int) -> int:
        if value < 1 or value > 100:
            raise ValueError("local job list limit must be between 1 and 100")
        return value


class ShowLocalJobRequest(CodeAlmanacModel):
    run_id: str

    @field_validator("run_id")
    @classmethod
    def require_run_id(cls, value: str) -> str:
        return required_text(value, "local job id")


class ReadLocalJobLogsRequest(CodeAlmanacModel):
    run_id: str

    @field_validator("run_id")
    @classmethod
    def require_run_id(cls, value: str) -> str:
        return required_text(value, "local job id")
