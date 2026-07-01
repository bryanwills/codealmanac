import httpx

from codealmanac.integrations.sources.web.client import fetch_web_response
from codealmanac.integrations.sources.web.documents import parse_web_response
from codealmanac.integrations.sources.web.errors import (
    first_error_line,
    unavailable_runtime,
)
from codealmanac.integrations.sources.web.models import UnsupportedWebContentError
from codealmanac.integrations.sources.web.rendering import (
    render_web_runtime,
    web_runtime_title,
)
from codealmanac.services.sources.models import (
    SourceKind,
    SourceRef,
    SourceRuntime,
    SourceRuntimeStatus,
)
from codealmanac.services.sources.requests import InspectSourceRuntimeRequest

WEB_RUNTIME_TIMEOUT_SECONDS = 20
DEFAULT_MAX_BYTES = 2_000_000
DEFAULT_MAX_CHARS = 60_000


class WebSourceRuntimeAdapter:
    def __init__(
        self,
        client: httpx.Client | None = None,
        max_bytes: int = DEFAULT_MAX_BYTES,
        max_chars: int = DEFAULT_MAX_CHARS,
        timeout_seconds: int = WEB_RUNTIME_TIMEOUT_SECONDS,
    ):
        self.client = client
        self.max_bytes = max_bytes
        self.max_chars = max_chars
        self.timeout_seconds = timeout_seconds

    def supports(self, ref: SourceRef) -> bool:
        return ref.kind == SourceKind.WEB_URL

    def inspect(self, request: InspectSourceRuntimeRequest) -> SourceRuntime:
        if request.ref.kind != SourceKind.WEB_URL:
            return SourceRuntime(
                ref=request.ref,
                status=SourceRuntimeStatus.SKIPPED,
                title=f"Unsupported web source {request.ref.identity}",
            )
        if request.ref.url is None:
            return unavailable_runtime(
                request.ref,
                "Web URL unavailable",
                "web source requires a URL",
            )
        try:
            response = fetch_web_response(
                request.ref.url,
                client=self.client,
                max_bytes=self.max_bytes,
                timeout_seconds=self.timeout_seconds,
            )
            document = parse_web_response(response)
        except (httpx.HTTPError, UnsupportedWebContentError, ValueError) as error:
            return unavailable_runtime(
                request.ref,
                "Web URL unavailable",
                first_error_line(error),
            )

        content, truncated = render_web_runtime(document, self.max_chars)
        return SourceRuntime(
            ref=request.ref,
            status=SourceRuntimeStatus.AVAILABLE,
            title=web_runtime_title(document),
            content=content,
            truncated=truncated or document.response_truncated,
        )
