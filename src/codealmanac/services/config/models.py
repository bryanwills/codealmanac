from datetime import timedelta
from enum import StrEnum

from humanfriendly import InvalidTimespan, parse_timespan
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.harnesses.models import HarnessKind

DEFAULT_HARNESS = HarnessKind.CODEX
DEFAULT_SYNC_QUIET = timedelta(minutes=45)
DEFAULT_AUTO_COMMIT = True


class ConfigKey(StrEnum):
    AUTO_COMMIT = "auto_commit"
    HARNESS_DEFAULT = "harness.default"
    SYNC_QUIET = "sync.quiet"


class HarnessConfig(CodeAlmanacModel):
    default: HarnessKind = DEFAULT_HARNESS


class SyncConfig(CodeAlmanacModel):
    quiet: timedelta = DEFAULT_SYNC_QUIET

    @field_validator("quiet", mode="before")
    @classmethod
    def parse_quiet(cls, value: object) -> object:
        return parse_duration(value, "sync.quiet")

    @field_validator("quiet")
    @classmethod
    def require_non_negative_quiet(cls, value: timedelta) -> timedelta:
        if value.total_seconds() < 0:
            raise ValueError("sync.quiet must be zero or greater")
        return value


class CodeAlmanacConfig(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, extra="forbid")

    auto_commit: bool = DEFAULT_AUTO_COMMIT
    harness: HarnessConfig = Field(default_factory=HarnessConfig)
    sync: SyncConfig = Field(default_factory=SyncConfig)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (init_settings,)


def parse_duration(value: object, label: str) -> object:
    if value is None or isinstance(value, timedelta):
        return value
    if not isinstance(value, str):
        return value
    try:
        return timedelta(seconds=parse_timespan(value))
    except InvalidTimespan as error:
        raise ValueError(f"{label} must be a duration") from error


class ConfigSetResult(CodeAlmanacModel):
    path: str
    key: ConfigKey
    value: str
