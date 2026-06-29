# Slice 45 - Viewer Wikilink Token Safety

## Scope

Close the local viewer risk that wikilink rendering could rewrite code spans or
fenced code blocks.

This slice does not change the public viewer route shape. It locks the existing
renderer contract with focused tests and records the boundary.

## Shape

```text
Markdown body
  -> markdown-it-py token stream
  -> rewrite inline child tokens where token.type == "text"
  -> markdown-it-py renderer
```

The renderer never rewrites raw HTML output. It creates Markdown tokens and lets
the renderer escape text and labels.

## Behavior

- text `[[page-link]]` becomes a local page link
- inline code `` `[[inline-code]]` `` remains code text
- fenced code containing `[[fenced-code]]` remains code text
- HTML in a wikilink label is escaped by the Markdown renderer

## Cosmic Python Note

Chapter 4 shaped the verification boundary. The viewer service owns the read
use case, while `MarkdownRenderer` owns Markdown rendering mechanics. Tests
exercise both the small renderer contract and the service/server read edges.

## Dependency Check

The project already depends on `markdown-it-py`, which exposes the parsed
Markdown token stream. That is the right structured contract here; no regex
over rendered HTML and no new Markdown parser are needed.

## Verification

- focused viewer tests:
  `uv run pytest tests/test_viewer_renderer.py tests/test_viewer_service.py tests/test_server.py`
- focused lint:
  `uv run ruff check src/codealmanac/services/viewer tests/test_viewer_renderer.py tests/test_viewer_service.py tests/test_server.py`
