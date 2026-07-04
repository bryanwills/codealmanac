from datetime import datetime, timedelta
from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text


class DrainRunQueueRequest(CodeAlmanacModel):
    cwd: Path
    wiki: str | None = None
    owner: str = "codealmanac-worker"
    pid: int | None = None
    now: datetime | None = None
    stale_after: timedelta = timedelta(minutes=30)
    max_runs: int | None = None

    @field_validator("owner")
    @classmethod
    def require_owner(cls, value: str) -> str:
        return required_text(value, "run queue owner")

    @field_validator("pid")
    @classmethod
    def positive_pid(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("run queue pid must be positive")
        return value

    @field_validator("stale_after")
    @classmethod
    def positive_stale_after(cls, value: timedelta) -> timedelta:
        if value.total_seconds() <= 0:
            raise ValueError("run queue stale_after must be positive")
        return value

    @field_validator("max_runs")
    @classmethod
    def positive_max_runs(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("max_runs must be positive")
        return value
