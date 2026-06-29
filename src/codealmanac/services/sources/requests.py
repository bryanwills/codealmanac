from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.sources.models import SourceRef, TranscriptApp


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

    @field_validator("apps")
    @classmethod
    def require_apps(
        cls,
        value: tuple[TranscriptApp, ...],
    ) -> tuple[TranscriptApp, ...]:
        if len(value) == 0:
            raise ValueError("at least one transcript app is required")
        return value


class InspectSourceRuntimeRequest(CodeAlmanacModel):
    cwd: Path
    ref: SourceRef
