# Slice 78 - Structured Page Sources Read Model

Date: 2026-07-01

## Scope

Make structured page `sources:` part of the Python read model:

- parse supported structured source entries from page frontmatter
- keep page markdown frontmatter as the source of truth
- derive file references from `sources[type=file]` so `search --mentions` works
- project page sources into SQLite as `page_sources`
- expose sources through `show --meta`, `show --json`, and viewer page APIs
- render sources in the local viewer side panel
- add health categories for missing citations, unused sources, and duplicate source ids

This slice does **not** add `migrate legacy-sources`, a public `sources` query
command, source snapshots, web fetching, source-currentness scoring, or the
archive-era review command family.

## Why Now

The live agreement says structured page `sources:` are not optional prompt
advice. They are the page evidence model. Current Python code only parses legacy
`files:` and inline file wikilinks, so file-aware search and page readback ignore
canonical `sources[type=file]` entries.

## Shape

```python
frontmatter = parse_frontmatter(raw)
document = PageDocument(
    sources=frontmatter.sources,
    file_refs=file_refs_from_legacy_files_and_file_sources(...),
)
```

The SQLite projection remains derived state:

```sql
page_sources(page_slug, source_id, source_type, target, title, retrieved_at, note)
```

Viewer and CLI consume `PageSource` from `PageView`; they do not reread markdown
frontmatter.

## Decisions

- Supported source types for this slice are `file`, `web`, `commit`, `pr`,
  `issue`, `conversation`, `wiki`, and `manual`.
- `target` is a display/query projection. It is not the full typed source
  object. Type-specific fields stay in frontmatter for now.
- File sources derive `file_refs`; legacy `files:` still derive refs too.
- Duplicate source ids stay visible because `page_sources` stores every
  parsed source row with its frontmatter order; health groups by page and
  source id to report duplicates.
- Citation markers are page-local `[@source-id]` markers in body prose.
- Health warnings are report-only. No migration or body citation insertion is
  added.

## Cosmic Python Transfer

Chapter 2 says the model should have "no dependencies whatsoever," so page
source normalization belongs in wiki/domain code before SQLite projection.
Chapter 4 says the service layer defines the system use cases; read commands and
viewer APIs should consume the indexed `PageView` instead of parsing markdown at
the edges. Chapter 6 frames Unit of Work as atomic operations; index replacement
continues to write pages, sources, refs, links, and metadata inside one SQLite
transaction.

## Files

- `src/codealmanac/services/wiki/models.py`
- `src/codealmanac/services/wiki/frontmatter.py`
- `src/codealmanac/services/wiki/documents.py`
- `src/codealmanac/services/index/models.py`
- `src/codealmanac/services/index/store.py`
- `src/codealmanac/services/index/views.py`
- `src/codealmanac/services/viewer/models.py`
- `src/codealmanac/services/viewer/service.py`
- `src/codealmanac/server/assets/viewer/renderers.js`
- `src/codealmanac/server/assets/viewer/components.js`
- `src/codealmanac/cli/render/root.py`
- focused tests under `tests/test_read_model.py`, `tests/test_topics_health.py`,
  `tests/test_viewer_service.py`, `tests/test_server.py`, and public contract docs.

## Verification

Focused:

```bash
uv run pytest tests/test_read_model.py tests/test_topics_health.py tests/test_viewer_service.py tests/test_server.py tests/test_public_contract.py
uv run ruff check src/codealmanac/services/wiki src/codealmanac/services/index src/codealmanac/services/viewer src/codealmanac/server src/codealmanac/cli tests/test_read_model.py tests/test_topics_health.py tests/test_viewer_service.py tests/test_server.py tests/test_public_contract.py
```

Broad:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
