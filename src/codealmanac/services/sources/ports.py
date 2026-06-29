from typing import Protocol

from codealmanac.services.sources.models import TranscriptApp, TranscriptCandidate
from codealmanac.services.sources.requests import DiscoverTranscriptsRequest


class TranscriptDiscoveryAdapter(Protocol):
    app: TranscriptApp

    def discover(
        self,
        request: DiscoverTranscriptsRequest,
    ) -> tuple[TranscriptCandidate, ...]:
        """Return local transcript candidates for one supported agent app."""
