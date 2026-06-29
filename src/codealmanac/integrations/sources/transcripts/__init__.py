from codealmanac.integrations.sources.transcripts.claude import (
    ClaudeTranscriptDiscoveryAdapter,
)
from codealmanac.integrations.sources.transcripts.codex import (
    CodexTranscriptDiscoveryAdapter,
)
from codealmanac.services.sources.ports import TranscriptDiscoveryAdapter


def default_transcript_discovery_adapters() -> tuple[TranscriptDiscoveryAdapter, ...]:
    return (
        ClaudeTranscriptDiscoveryAdapter(),
        CodexTranscriptDiscoveryAdapter(),
    )


__all__ = [
    "ClaudeTranscriptDiscoveryAdapter",
    "CodexTranscriptDiscoveryAdapter",
    "default_transcript_discovery_adapters",
]
