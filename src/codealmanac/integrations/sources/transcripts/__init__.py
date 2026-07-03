from codealmanac.engine.sources.ports import (
    SourceRuntimeAdapter,
    TranscriptDiscoveryAdapter,
)
from codealmanac.integrations.sources.transcripts.claude import (
    ClaudeTranscriptDiscoveryAdapter,
)
from codealmanac.integrations.sources.transcripts.codex import (
    CodexTranscriptDiscoveryAdapter,
)
from codealmanac.integrations.sources.transcripts.runtime import (
    TranscriptSourceRuntimeAdapter,
)


def default_transcript_discovery_adapters() -> tuple[TranscriptDiscoveryAdapter, ...]:
    return (
        ClaudeTranscriptDiscoveryAdapter(),
        CodexTranscriptDiscoveryAdapter(),
    )


def default_transcript_runtime_adapters() -> tuple[SourceRuntimeAdapter, ...]:
    return (TranscriptSourceRuntimeAdapter(),)


__all__ = [
    "ClaudeTranscriptDiscoveryAdapter",
    "CodexTranscriptDiscoveryAdapter",
    "TranscriptSourceRuntimeAdapter",
    "default_transcript_discovery_adapters",
    "default_transcript_runtime_adapters",
]
