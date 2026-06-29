from typing import Protocol

from codealmanac.services.sources.models import (
    SourceRef,
    SourceRuntime,
    TranscriptApp,
    TranscriptCandidate,
)
from codealmanac.services.sources.requests import (
    DiscoverTranscriptsRequest,
    InspectSourceRuntimeRequest,
)


class TranscriptDiscoveryAdapter(Protocol):
    app: TranscriptApp

    def discover(
        self,
        request: DiscoverTranscriptsRequest,
    ) -> tuple[TranscriptCandidate, ...]:
        """Return local transcript candidates for one supported agent app."""


class SourceRuntimeAdapter(Protocol):
    def supports(self, ref: SourceRef) -> bool:
        """Return true when this adapter can inspect the source ref."""

    def inspect(self, request: InspectSourceRuntimeRequest) -> SourceRuntime:
        """Return bounded runtime material for one source ref."""
