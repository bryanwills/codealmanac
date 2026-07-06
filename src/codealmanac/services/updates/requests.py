from datetime import datetime, timedelta

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel

DEFAULT_UPDATE_LOCK_STALE_AFTER = timedelta(minutes=30)


class CheckUpdateRequest(CodeAlmanacModel):
    pass


class RunUpdateRequest(CodeAlmanacModel):
    scheduled: bool = False
    now: datetime | None = None
    lock_stale_after: timedelta = DEFAULT_UPDATE_LOCK_STALE_AFTER

    @field_validator("lock_stale_after")
    @classmethod
    def positive_lock_stale_after(cls, value: timedelta) -> timedelta:
        if value.total_seconds() <= 0:
            raise ValueError("update lock stale_after must be positive")
        return value
