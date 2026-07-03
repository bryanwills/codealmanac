from collections.abc import Sequence

from codealmanac.engine.sources.address_resolution import resolve_address
from codealmanac.engine.sources.models import (
    SourceAddress,
    SourceBrief,
    SourceRuntime,
    SourceRuntimeStatus,
    TranscriptCandidate,
)
from codealmanac.engine.sources.ports import (
    SourceRuntimeAdapter,
    TranscriptDiscoveryAdapter,
)
from codealmanac.engine.sources.requests import (
    DiscoverTranscriptsRequest,
    InspectSourceRuntimeRequest,
    ResolveSourcesRequest,
)
from codealmanac.engine.sources.transcripts import transcript_sort_key


class SourcesService:
    def __init__(
        self,
        transcript_discovery_adapters: Sequence[TranscriptDiscoveryAdapter] = (),
        runtime_adapters: Sequence[SourceRuntimeAdapter] = (),
    ):
        self.transcript_discovery_adapters = tuple(transcript_discovery_adapters)
        self.runtime_adapters = tuple(runtime_adapters)

    def resolve(self, request: ResolveSourcesRequest) -> tuple[SourceBrief, ...]:
        return tuple(
            resolve_address(SourceAddress(raw=raw), request.cwd)
            for raw in request.inputs
        )

    def discover_transcripts(
        self,
        request: DiscoverTranscriptsRequest,
    ) -> tuple[TranscriptCandidate, ...]:
        selected = set(request.apps)
        candidates: list[TranscriptCandidate] = []
        for adapter in self.transcript_discovery_adapters:
            if adapter.app in selected:
                candidates.extend(adapter.discover(request))
        return tuple(sorted(candidates, key=transcript_sort_key))

    def inspect_runtime(
        self,
        request: InspectSourceRuntimeRequest,
    ) -> SourceRuntime:
        for adapter in self.runtime_adapters:
            if adapter.supports(request.ref):
                return adapter.inspect(request)
        return SourceRuntime(
            ref=request.ref,
            status=SourceRuntimeStatus.SKIPPED,
            title=f"No runtime adapter for {request.ref.identity}",
        )
