# Slice 9 Review Fix: Stale-Aware Index Refresh

## Finding

`serve` exposed a bad read-path cost: `ViewerService` assembled overview, page,
topic, and search payloads by calling several index-backed read verbs, and every
read verb called `ensure_fresh`. Before this fix, `ensure_fresh` forced a full
SQLite projection rebuild even when the source markdown and `topics.yaml` were
unchanged.

## Decision

`IndexService.ensure_fresh` now means stale-aware refresh. It parses the source
wiki, computes a source signature from indexed page fingerprints and
`topics.yaml`, compares that signature to `index_metadata`, and skips SQLite
projection writes when unchanged.

`IndexService.reindex` remains the explicit forced rebuild path. This preserves
the CLI contract that `codealmanac reindex` is the escape hatch for rebuilding
the derived read model.

## Cosmic Python Pressure

Cosmic Python chapter 12 separates read-side and write-side concerns. For
CodeAlmanac, committed markdown is the write-side truth and `.almanac/index.db`
is a derived read model. The viewer is a query adapter over that read model;
projection refresh belongs inside the index service, not in the server or
viewer edge.

## Tests

- Focused regression: unchanged `ensure_fresh` returns `changed=0` and a SQLite
  trigger proves it does not delete/reinsert `pages`.
- Edit regression: changing a page updates the signature and rewrites the
  projection.
- Forced rebuild regression: `reindex` still rewrites the projection when the
  index is already fresh.

## Remaining Risk

`refresh` still parses source markdown to compute the signature. That is a
bounded correctness-first cost for this slice. A future large-repo optimization
can add a cheaper filesystem stat manifest if real dogfood shows source parsing
is too slow.
