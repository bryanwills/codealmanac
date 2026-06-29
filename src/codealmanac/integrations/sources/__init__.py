from codealmanac.integrations.sources.git import GitSourceRuntimeAdapter
from codealmanac.integrations.sources.github import GitHubSourceRuntimeAdapter
from codealmanac.integrations.sources.transcripts import (
    TranscriptSourceRuntimeAdapter,
    default_transcript_discovery_adapters,
)
from codealmanac.integrations.sources.web import WebSourceRuntimeAdapter
from codealmanac.services.sources.ports import SourceRuntimeAdapter


def default_source_runtime_adapters() -> tuple[SourceRuntimeAdapter, ...]:
    return (
        GitSourceRuntimeAdapter(),
        GitHubSourceRuntimeAdapter(),
        TranscriptSourceRuntimeAdapter(),
        WebSourceRuntimeAdapter(),
    )

__all__ = [
    "GitSourceRuntimeAdapter",
    "GitHubSourceRuntimeAdapter",
    "TranscriptSourceRuntimeAdapter",
    "WebSourceRuntimeAdapter",
    "default_source_runtime_adapters",
    "default_transcript_discovery_adapters",
]
