from datetime import datetime, timedelta
from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.sources.models import TranscriptApp


class RunSyncStatusRequest(CodeAlmanacModel):
    cwd: Path
    apps: tuple[TranscriptApp, ...]
    quiet: timedelta
    wiki: str | None = None
    home: Path | None = None
    now: datetime | None = None

    @field_validator("apps")
    @classmethod
    def require_apps(
        cls,
        value: tuple[TranscriptApp, ...],
    ) -> tuple[TranscriptApp, ...]:
        if len(value) == 0:
            raise ValueError("at least one sync app is required")
        return value

    @field_validator("quiet")
    @classmethod
    def non_negative_quiet(cls, value: timedelta) -> timedelta:
        if value.total_seconds() < 0:
            raise ValueError("quiet duration must be non-negative")
        return value
