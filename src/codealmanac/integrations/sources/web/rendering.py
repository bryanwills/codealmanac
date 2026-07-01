from codealmanac.integrations.sources.runtime import (
    bounded_text,
    source_runtime_section,
)
from codealmanac.integrations.sources.web.models import WebRuntimeDocument


def render_web_runtime(
    document: WebRuntimeDocument,
    max_chars: int,
) -> tuple[str, bool]:
    return bounded_text(
        "\n\n".join(
            (
                source_runtime_section("metadata", render_metadata(document)),
                source_runtime_section("content", document.body),
            )
        ),
        max_chars,
    )


def web_runtime_title(document: WebRuntimeDocument) -> str:
    title_suffix = f": {document.title}" if document.title is not None else ""
    return f"Web URL {document.final_url}{title_suffix}"


def render_metadata(document: WebRuntimeDocument) -> str:
    lines = [
        f"final_url: {document.final_url}",
        f"status_code: {document.status_code}",
        f"content_type: {document.content_type}",
        f"content_kind: {document.content_kind.value}",
        f"response_truncated: {str(document.response_truncated).lower()}",
    ]
    if document.title is not None:
        lines.append(f"title: {document.title}")
    return "\n".join(lines)
