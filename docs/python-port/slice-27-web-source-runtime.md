# Slice 27 - Web Source Runtime

Date: 2026-06-29

## Scope

Add bounded readable runtime material for generic `SourceKind.WEB_URL` refs.

This slice completes the MVP source-runtime set named in the live agreement:
Git, GitHub, transcripts, and web URLs. It does not add a browser crawler,
semantic extraction engine, hosted source library, durable source catalog, or a
new public CLI verb.

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `docs/python-port-live-agreement.md`
- `docs/reference/cosmic-python/CODEALMANAC.md`
- `docs/reference/cosmic-python/chapter_11_external_events.md`
- `docs/reference/cosmic-python/chapter_13_dependency_injection.md`
- Official `httpx` docs for client requests, timeouts, redirects, and mock
  transports
- Official Beautiful Soup docs for HTML parsing and text extraction

## Design

`SourcesService` already classifies generic HTTP(S) URLs as `WEB_URL`, and
`IngestWorkflow` already asks source runtime adapters for bounded snapshots
without branching on source kind. Web material fits that seam.

```python
brief = app.sources.resolve(... "https://example.com/post" ...)
runtime = app.sources.inspect_runtime(InspectSourceRuntimeRequest(ref=brief.ref))
prompt = render_ingest_prompt(..., source_runtime=(runtime,))
```

The new concrete adapter lives at `integrations/sources/web/adapter.py` and
implements `SourceRuntimeAdapter`.

The adapter:

- fetches the URL with `httpx`
- follows redirects
- bounds response bytes before parsing
- supports HTML and text-like content types
- strips script/style/noscript/template/svg nodes from HTML
- renders metadata plus readable content through the existing source-runtime
  section helper
- returns `unavailable` snapshots for HTTP failures, network failures, missing
  URLs, and unsupported binary content

## Library Choices

Use `httpx` as a runtime dependency because HTTP fetching is a famous library
problem and `httpx` gives a typed client surface, redirects, timeouts, streaming,
and `MockTransport` for tests.

Use `beautifulsoup4` for basic HTML-to-text extraction. This slice needs
readable source material for an agent prompt, not full browser rendering,
JavaScript execution, or article-readability heuristics.

## Tests

- New `tests/test_web_source_runtime.py`
  - HTML extraction removes script/style content
  - plain text passes through
  - HTTP errors become `unavailable`
  - unsupported content types become `unavailable`
  - runtime text is bounded
- Extend `tests/test_ingest_workflow.py`
  - a real `WebSourceRuntimeAdapter` with `httpx.MockTransport` feeds web
    runtime material into the ingest prompt
- Keep `tests/test_architecture.py` green
  - services/workflows/CLI still do not import concrete integrations

## Verification Plan

Focused:

```bash
uv run pytest tests/test_web_source_runtime.py tests/test_sources_service.py tests/test_ingest_workflow.py tests/test_architecture.py
uv run ruff check src/codealmanac/integrations/sources tests/test_web_source_runtime.py tests/test_ingest_workflow.py
```

Full:

```bash
uv run pytest
uv run ruff check src tests
git diff --check
uv build --out-dir /tmp/codealmanac-build-slice27
```

Dogfood:

- temp Git repo
- real default `WebSourceRuntimeAdapter`
- real public URL
- fake harness that writes one wiki page
- assert the prompt contains fetched web content and search finds the written
  page
