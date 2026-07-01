# Slice 98 - Index Read View Boundaries

Date: 2026-07-01

## Scope

Split the SQLite index read side into modules by query family:

- search and file-mention query construction
- summary counts
- page detail projection
- topic DAG read projection
- health and integrity findings

This slice does not change the index schema, page parsing, public CLI output, or
viewer API shape.

## Why Now

`services/index/views.py` had become the largest Python file in the active
implementation. The write/read split is already a good fit for Cosmic Python's
CQRS guidance, but one 627-line read file was becoming a second catchall.

The index read model is now used by search/show/topics/health and by `serve`.
Those readers have different reasons to change. Keeping them in one module
makes a future health rule, FTS tweak, or page projection change harder to
review.

## Decisions

- Keep `IndexStore` as the store facade.
- Keep `services/index/views.py` as a small compatibility facade.
- Add `search_views.py`, `summary_views.py`, `page_views.py`,
  `topic_views.py`, and `health_views.py`.
- Keep read-side SQL out of `store.py`; keep write/migration SQL out of the
  view modules.
- Keep shared page helpers local to `page_views.py` unless a second module
  needs a broader abstraction.

## Shape

```python
# store facade remains unchanged
return search_pages(connection, request)

# views.py re-exports query-family functions
from codealmanac.services.index.search_views import search_pages
from codealmanac.services.index.summary_views import index_counts
from codealmanac.services.index.page_views import get_page_view
from codealmanac.services.index.topic_views import get_topic_detail
from codealmanac.services.index.health_views import build_health_report
```

## Cosmic Python Transfer

Chapter 12 says reads and writes are different and should be treated
differently. The current project already follows that by keeping projection
writes in `store.py` and query views in `views.py`; this slice applies the same
idea inside the read side.

## Files

- `src/codealmanac/services/index/views.py`
- `src/codealmanac/services/index/search_views.py`
- `src/codealmanac/services/index/summary_views.py`
- `src/codealmanac/services/index/page_views.py`
- `src/codealmanac/services/index/topic_views.py`
- `src/codealmanac/services/index/health_views.py`
- `tests/test_architecture.py`
- `docs/python-port-live-agreement.md`
- `docs/python-port/idea-evolution.md`
- `docs/python-port/ownership-map.md`
- `docs/python-port/next-agent-brief.md`

## Verification

Focused:

```bash
uv run pytest tests/test_read_model.py tests/test_topics_health.py tests/test_viewer_service.py tests/test_server.py tests/test_architecture.py
uv run ruff check src/codealmanac/services/index tests/test_read_model.py tests/test_topics_health.py tests/test_viewer_service.py tests/test_server.py tests/test_architecture.py
```

Broad:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
