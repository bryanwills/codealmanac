from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.sources.models import SourceRef, TranscriptApp
from codealmanac.services.workspaces.roots import (
    DEFAULT_ALMANAC_ROOT,
    normalized_almanac_roots,
)


class ResolveSourcesRequest(CodeAlmanacModel):
    cwd: Path
    inputs: tuple[str, ...]

    @field_validator("inputs")
    @classmethod
    def require_inputs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) == 0:
            raise ValueError("at least one source input is required")
        return value


class DiscoverTranscriptsRequest(CodeAlmanacModel):
    home: Path
    apps: tuple[TranscriptApp, ...]
    almanac_roots: tuple[Path, ...] = (DEFAULT_ALMANAC_ROOT,)

    @field_validator("apps")
    @classmethod
    def require_apps(
        cls,
        value: tuple[TranscriptApp, ...],
    ) -> tuple[TranscriptApp, ...]:
        if len(value) == 0:
            raise ValueError("at least one transcript app is required")
        return value

    @field_validator("almanac_roots")
    @classmethod
    def validate_almanac_roots(cls, value: tuple[Path, ...]) -> tuple[Path, ...]:
        return normalized_almanac_roots(value)


class InspectSourceRuntimeRequest(CodeAlmanacModel):
    cwd: Path
    ref: SourceRef
