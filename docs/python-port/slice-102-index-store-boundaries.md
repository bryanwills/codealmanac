# Slice 102: Index Store Boundaries

## Scope

Split the SQLite index write side into explicit modules without changing user
behavior:

- `schema.py` owns index schema versioning, DDL, migrations, and opening an
  initialized `index.db` connection.
- `sources.py` owns loading markdown pages, loading `topics.yaml`, counting
  skipped files, and constructing freshness signatures.
- `projection.py` owns replacing the derived SQLite projection, persisting the
  source signature, and inserting page/topic rows.
- `store.py` stays the service-facing facade used by `IndexService`.

## Out Of Scope

- No index schema changes.
- No query behavior changes.
- No source-frontmatter model changes.
- No performance optimization beyond preserving the existing signature skip.

## Design Notes

Current `store.py` mixes facade methods, schema DDL, migration setup, markdown
source loading, freshness checks, and projection writes. That worked while the
index was small, but now it is the largest production file and new source,
health, and view behavior has made the reasons-to-change visible.

Cosmic Python frames repositories as "an abstraction over persistent storage"
that hides data-access details from the service layer
(`docs/reference/cosmic-python/chapter_02_repository.md`). For this slice, the
public abstraction remains `IndexStore`; the internal split keeps the
persistence details honest. The CQRS chapter also says to ask whether we can
"build a simpler read model" and notes that rebuilding a view model is easy from
source data (`docs/reference/cosmic-python/chapter_12_cqrs.md`). The index is
exactly that kind of derived read model: markdown plus `topics.yaml` are truth,
`index.db` is the replaceable projection.

## Files

- `src/codealmanac/services/index/store.py`
- `src/codealmanac/services/index/schema.py`
- `src/codealmanac/services/index/sources.py`
- `src/codealmanac/services/index/projection.py`
- `tests/test_architecture.py`
- `docs/python-port-live-agreement.md`
- `docs/python-port/ownership-map.md`
- `docs/python-port/idea-evolution.md`
- `docs/python-port/next-agent-brief.md`
- `docs/python-port/verification-matrix.md`
- `docs/python-port/worklog.md`
- `.almanac/pages/sqlite-indexer.md`

## Tests

- Architecture guard: `store.py` remains a facade and index write-side modules
  own schema/source/projection responsibilities separately.
- Focused read-model tests around freshness skip and forced reindex.
- Full `uv run pytest`.
- Full `uv run ruff check .`.

