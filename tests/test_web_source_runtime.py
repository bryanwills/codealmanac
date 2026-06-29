from pathlib import Path

import httpx

from codealmanac.app import create_app
from codealmanac.integrations.sources.web import WebSourceRuntimeAdapter
from codealmanac.services.sources.models import SourceRuntimeStatus
from codealmanac.services.sources.requests import (
    InspectSourceRuntimeRequest,
    ResolveSourcesRequest,
)


def test_web_source_runtime_extracts_html_text(tmp_path: Path):
    app = create_app(source_runtime_adapters=(web_adapter(ARTICLE_HTML),))
    (brief,) = app.sources.resolve(
        ResolveSourcesRequest(cwd=tmp_path, inputs=("https://example.test/article",))
    )

    runtime = app.sources.inspect_runtime(
        InspectSourceRuntimeRequest(cwd=tmp_path, ref=brief.ref)
    )

    assert runtime.status == SourceRuntimeStatus.AVAILABLE
    assert runtime.title == "Web URL https://example.test/article: Design Notes"
    assert "content_kind: html" in (runtime.content or "")
    assert "title: Design Notes" in (runtime.content or "")
    assert "Persist the decision in the wiki." in (runtime.content or "")
    assert "console.log" not in (runtime.content or "")
    assert "body { color: red; }" not in (runtime.content or "")


def test_web_source_runtime_reads_plain_text(tmp_path: Path):
    app = create_app(
        source_runtime_adapters=(
            web_adapter(
                "deploy invariant\nkeep the rollout note",
                content_type="text/plain; charset=utf-8",
            ),
        )
    )
    (brief,) = app.sources.resolve(
        ResolveSourcesRequest(cwd=tmp_path, inputs=("https://example.test/note.txt",))
    )

    runtime = app.sources.inspect_runtime(
        InspectSourceRuntimeRequest(cwd=tmp_path, ref=brief.ref)
    )

    assert runtime.status == SourceRuntimeStatus.AVAILABLE
    assert runtime.title == "Web URL https://example.test/note.txt"
    assert "content_kind: text" in (runtime.content or "")
    assert "deploy invariant" in (runtime.content or "")
    assert "keep the rollout note" in (runtime.content or "")


def test_web_source_runtime_marks_http_errors_unavailable(tmp_path: Path):
    app = create_app(
        source_runtime_adapters=(
            web_adapter("missing", status_code=404, content_type="text/plain"),
        )
    )
    (brief,) = app.sources.resolve(
        ResolveSourcesRequest(cwd=tmp_path, inputs=("https://example.test/missing",))
    )

    runtime = app.sources.inspect_runtime(
        InspectSourceRuntimeRequest(cwd=tmp_path, ref=brief.ref)
    )

    assert runtime.status == SourceRuntimeStatus.UNAVAILABLE
    assert runtime.content is None
    assert len(runtime.diagnostics) == 1
    assert "404" in runtime.diagnostics[0]


def test_web_source_runtime_marks_unsupported_content_unavailable(tmp_path: Path):
    app = create_app(
        source_runtime_adapters=(
            web_adapter("%PDF-1.7", content_type="application/pdf"),
        )
    )
    (brief,) = app.sources.resolve(
        ResolveSourcesRequest(cwd=tmp_path, inputs=("https://example.test/file.pdf",))
    )

    runtime = app.sources.inspect_runtime(
        InspectSourceRuntimeRequest(cwd=tmp_path, ref=brief.ref)
    )

    assert runtime.status == SourceRuntimeStatus.UNAVAILABLE
    assert runtime.content is None
    assert runtime.diagnostics == ("unsupported web content type: application/pdf",)


def test_web_source_runtime_truncates_runtime_text(tmp_path: Path):
    app = create_app(
        source_runtime_adapters=(
            web_adapter(
                "<html><body><p>old context</p><p>new context</p></body></html>",
                max_chars=180,
            ),
        )
    )
    (brief,) = app.sources.resolve(
        ResolveSourcesRequest(cwd=tmp_path, inputs=("https://example.test/long",))
    )

    runtime = app.sources.inspect_runtime(
        InspectSourceRuntimeRequest(cwd=tmp_path, ref=brief.ref)
    )

    assert runtime.status == SourceRuntimeStatus.AVAILABLE
    assert runtime.truncated is True
    assert "[truncated]" in (runtime.content or "")


def web_adapter(
    body: str,
    *,
    content_type: str = "text/html; charset=utf-8",
    status_code: int = 200,
    max_chars: int = 60_000,
) -> WebSourceRuntimeAdapter:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code,
            headers={"content-type": content_type},
            text=body,
            request=request,
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    return WebSourceRuntimeAdapter(client=client, max_chars=max_chars)


ARTICLE_HTML = """<!doctype html>
<html>
  <head>
    <title>Design Notes</title>
    <style>body { color: red; }</style>
  </head>
  <body>
    <h1>Design Notes</h1>
    <p>Persist the decision in the wiki.</p>
    <script>console.log("ignore me")</script>
  </body>
</html>
"""
