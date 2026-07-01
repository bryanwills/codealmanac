from bs4 import BeautifulSoup

from codealmanac.integrations.sources.web.models import (
    FetchedWebResponse,
    UnsupportedWebContentError,
    WebContentKind,
    WebRuntimeDocument,
)


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
