from uuid import UUID

from pydantic import Field, field_validator

from codealmanac.core.models import CodeAlmanacModel


class ListCloudRunsForRepoRequest(CodeAlmanacModel):
    api_url: str = Field(min_length=1)
    repo_id: int = Field(gt=0)
    limit: int | None = None
    cursor: str | None = None

    @field_validator("limit")
    @classmethod
    def positive_limit(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("limit must be positive")
        return value


class ReadCloudRunRequest(CodeAlmanacModel):
    api_url: str = Field(min_length=1)
    run_id: UUID


class ListCloudRunEventsRequest(CodeAlmanacModel):
    api_url: str = Field(min_length=1)
    run_id: UUID
