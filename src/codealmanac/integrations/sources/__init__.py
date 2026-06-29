from codealmanac.integrations.sources.git import GitSourceRuntimeAdapter
from codealmanac.integrations.sources.transcripts import (
    default_transcript_discovery_adapters,
)
from codealmanac.services.sources.ports import SourceRuntimeAdapter


def default_source_runtime_adapters() -> tuple[SourceRuntimeAdapter, ...]:
    return (GitSourceRuntimeAdapter(),)

__all__ = [
    "GitSourceRuntimeAdapter",
    "default_source_runtime_adapters",
    "default_transcript_discovery_adapters",
]
