from enum import StrEnum

import httpx
from bs4 import BeautifulSoup
from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.integrations.sources.runtime import (
    bounded_text,
    source_runtime_section,
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


class WebContentKind(StrEnum):
    HTML = "html"
    TEXT = "text"


class FetchedWebResponse(CodeAlmanacModel):
    final_url: str
    status_code: int
    content_type: str
    body: bytes
    response_truncated: bool = False

    @field_validator("final_url", "content_type")
    @classmethod
    def require_text_fields(cls, value: str) -> str:
        return required_text(value, "web response")

    @field_validator("status_code")
    @classmethod
    def validate_status_code(cls, value: int) -> int:
        if value < 100 or value > 599:
            raise ValueError("HTTP status code must be between 100 and 599")
        return value


class WebRuntimeDocument(CodeAlmanacModel):
    final_url: str
    status_code: int
    content_type: str
    content_kind: WebContentKind
    body: str
    title: str | None = None
    response_truncated: bool = False

    @field_validator("final_url", "content_type", "body")
    @classmethod
    def require_text_fields(cls, value: str) -> str:
        return required_text(value, "web runtime document")


class UnsupportedWebContentError(Exception):
    pass


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
            response = self._fetch(request.ref.url)
            document = parse_web_response(response)
        except (httpx.HTTPError, UnsupportedWebContentError, ValueError) as error:
            return unavailable_runtime(
                request.ref,
                "Web URL unavailable",
                first_error_line(error),
            )

        content, truncated = bounded_text(
            "\n\n".join(
                (
                    source_runtime_section("metadata", render_metadata(document)),
                    source_runtime_section("content", document.body),
                )
            ),
            self.max_chars,
        )
        title_suffix = f": {document.title}" if document.title is not None else ""
        return SourceRuntime(
            ref=request.ref,
            status=SourceRuntimeStatus.AVAILABLE,
            title=f"Web URL {document.final_url}{title_suffix}",
            content=content,
            truncated=truncated or document.response_truncated,
        )

    def _fetch(self, url: str) -> FetchedWebResponse:
        if self.client is not None:
            return fetch_with_client(
                self.client,
                url,
                self.max_bytes,
                self.timeout_seconds,
            )
        with httpx.Client(
            follow_redirects=True,
            timeout=self.timeout_seconds,
        ) as client:
            return fetch_with_client(
                client,
                url,
                self.max_bytes,
                self.timeout_seconds,
            )


def fetch_with_client(
    client: httpx.Client,
    url: str,
    max_bytes: int,
    timeout_seconds: int,
) -> FetchedWebResponse:
    with client.stream(
        "GET",
        url,
        follow_redirects=True,
        timeout=timeout_seconds,
    ) as response:
        response.raise_for_status()
        body, truncated = read_bounded_response(response, max_bytes)
        content_type = response.headers.get("content-type", "").strip()
        return FetchedWebResponse(
            final_url=str(response.url),
            status_code=response.status_code,
            content_type=content_type or "(none)",
            body=body,
            response_truncated=truncated,
        )


def read_bounded_response(
    response: httpx.Response,
    max_bytes: int,
) -> tuple[bytes, bool]:
    chunks: list[bytes] = []
    total = 0
    truncated = False
    for chunk in response.iter_bytes():
        remaining = max_bytes - total
        if remaining <= 0:
            truncated = True
            break
        if len(chunk) > remaining:
            chunks.append(chunk[:remaining])
            truncated = True
            break
        chunks.append(chunk)
        total += len(chunk)
    return b"".join(chunks), truncated


def parse_web_response(response: FetchedWebResponse) -> WebRuntimeDocument:
    content_kind = content_kind_for(response.content_type)
    text = decode_body(response.body)
    if content_kind == WebContentKind.HTML:
        return parse_html_document(response, text)
    return WebRuntimeDocument(
        final_url=response.final_url,
        status_code=response.status_code,
        content_type=response.content_type,
        content_kind=content_kind,
        body=normalized_text(text),
        response_truncated=response.response_truncated,
    )


def content_kind_for(content_type: str) -> WebContentKind:
    media_type = content_type.split(";", 1)[0].strip().casefold()
    if media_type in {"text/html", "application/xhtml+xml", "(none)"}:
        return WebContentKind.HTML
    if media_type.startswith("text/"):
        return WebContentKind.TEXT
    if media_type in {
        "application/json",
        "application/ld+json",
        "application/xml",
        "application/rss+xml",
        "application/atom+xml",
    }:
        return WebContentKind.TEXT
    raise UnsupportedWebContentError(f"unsupported web content type: {media_type}")


def parse_html_document(response: FetchedWebResponse, html: str) -> WebRuntimeDocument:
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(("script", "style", "noscript", "template", "svg")):
        element.decompose()
    title = title_text(soup)
    body = normalized_text(soup.get_text("\n"))
    if body == "":
        body = "(empty page text)"
    return WebRuntimeDocument(
        final_url=response.final_url,
        status_code=response.status_code,
        content_type=response.content_type,
        content_kind=WebContentKind.HTML,
        title=title,
        body=body,
        response_truncated=response.response_truncated,
    )


def decode_body(body: bytes) -> str:
    return body.decode("utf-8", errors="replace")


def title_text(soup: BeautifulSoup) -> str | None:
    if soup.title is None:
        return None
    title = normalized_text(soup.title.get_text(" "))
    if title == "":
        return None
    return title


def normalized_text(value: str) -> str:
    lines: list[str] = []
    previous_blank = False
    for raw_line in value.splitlines():
        line = " ".join(raw_line.strip().split())
        if line == "":
            if lines and not previous_blank:
                lines.append("")
            previous_blank = True
            continue
        lines.append(line)
        previous_blank = False
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


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


def unavailable_runtime(
    ref: SourceRef,
    title: str,
    diagnostic: str,
) -> SourceRuntime:
    return SourceRuntime(
        ref=ref,
        status=SourceRuntimeStatus.UNAVAILABLE,
        title=title,
        diagnostics=(diagnostic,),
    )


def first_error_line(error: Exception) -> str:
    lines = [line.strip() for line in str(error).splitlines() if line.strip()]
    if len(lines) == 0:
        return error.__class__.__name__
    return lines[0]
