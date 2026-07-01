# Slice 81 - Multi-Wiki Serve

Date: 2026-07-01

## Scope

Make `codealmanac serve` browse registered local wikis by default while keeping
`--wiki` as a narrowing flag:

- overview responses expose the selected wiki plus the available local wiki list
- page, topic, search, and file APIs accept a `wiki` query selector
- the viewer sidebar can switch between local wikis without restarting the server
- unavailable registry entries are skipped in the switcher instead of being dropped
- `serve --wiki <selector>` keeps the viewer narrowed to that one wiki

This slice does **not** add hosted wiki browsing, sticky `use` state, account
selection, source-code preview, or a React/Next.js viewer rewrite.

## Why Now

The live agreement says `serve` should browse all registered local wikis. The
current server closes over one `cwd` and optional `--wiki` selector, and every
viewer request resolves exactly one workspace. That preserves the old single
wiki behavior and leaves the multi-wiki requirement unimplemented.

## Shape

```python
overview = app.viewer.overview(
    ViewerOverviewRequest(cwd=cwd, wiki=requested_wiki, include_workspaces=True)
)

page = app.viewer.page(
    ViewerPageRequest(cwd=cwd, wiki=requested_wiki, slug=slug)
)
```

The server edge remains standard HTTP work:

```python
@server.get("/api/page/{slug}")
def page(slug: str, wiki: str | None = None) -> ViewerPage:
    return codealmanac.viewer.page(ViewerPageRequest(...))
```

The browser owns only presentation state:

```javascript
state.selectedWiki = overview.workspace.workspace_id;
viewerApi.page(slug, state.selectedWiki);
```

`ViewerService` owns the product scope:

- select the current/explicit workspace
- list available registered workspaces
- skip unavailable entries without mutating the registry
- return stable `workspace_id` values so duplicate names do not break switching

## Decisions

- Use `workspace_id` as the browser selector value. Names are user-facing labels,
  but the registry can contain ambiguous names.
- Keep existing response fields such as `workspace`, `pages`, and `topics` so the
  current frontend contract remains additive.
- Add `workspaces` only to overview. Detail routes already return their selected
  workspace, and the browser can keep the switcher data from overview.
- When no `--wiki` is passed, prefer the nearest current repo if one is
  resolvable; otherwise fall back to the first available registered local wiki.
- When `--wiki` is passed, only expose that selected wiki in overview. That makes
  `--wiki` a true narrowing flag instead of a starting suggestion.

## Cosmic Python Transfer

Chapter 4 says web endpoint responsibility is request parsing, status codes, and
JSON, with orchestration in the service layer
(`docs/reference/cosmic-python/chapter_04_service_layer.md`).

Chapter 12 says read-only views should be split from state-modifying paths
(`docs/reference/cosmic-python/chapter_12_cqrs.md`). This slice only changes
viewer read models and static assets.

Chapter 13 discusses app factories/composition roots
(`docs/reference/cosmic-python/chapter_13_dependency_injection.md`). The server
factory keeps receiving the composed `CodeAlmanac` app instead of constructing
services itself.

## Files

- `src/codealmanac/services/viewer/models.py`
- `src/codealmanac/services/viewer/requests.py`
- `src/codealmanac/services/viewer/service.py`
- `src/codealmanac/database/sqlite.py`
- `src/codealmanac/server/app.py`
- `src/codealmanac/server/assets/index.html`
- `src/codealmanac/server/assets/app.css`
- `src/codealmanac/server/assets/viewer/api.js`
- `src/codealmanac/server/assets/viewer/main.js`
- `src/codealmanac/server/assets/viewer/renderers.js`
- `tests/test_viewer_service.py`
- `tests/test_server.py`
- `tests/test_database.py`
- steering docs under `docs/python-port/`

## Verification

Focused:

```bash
uv run pytest tests/test_viewer_service.py tests/test_server.py
uv run ruff check src/codealmanac/services/viewer src/codealmanac/server tests/test_viewer_service.py tests/test_server.py
```

Broad:

```bash
uv run pytest
uv run ruff check .
git diff --check
```

Dogfood:

```bash
HOME="$(mktemp -d)" uv run codealmanac init /tmp/wiki-a
HOME="$HOME" uv run codealmanac init /tmp/wiki-b
HOME="$HOME" uv run codealmanac serve --host 127.0.0.1 --port <free-port>
curl http://127.0.0.1:<free-port>/api/overview
```
