# Slice 7: Build And Reindex Commands

## Scope

Add deterministic local maintenance commands:

```text
codealmanac build [path]
codealmanac reindex [--wiki <name>]
```

`build` refreshes the repo-owned wiki scaffold and rebuilds the derived SQLite
index. `reindex` forces a full rebuild of `.almanac/index.db`.

## Product Semantics

`build` is local-only in this Python slice. It does not invoke AI and does not
write page prose beyond deterministic starter scaffold files. It exists because
the public CLI contract names `build`, and because `init` already uses the build
workflow internally.

`reindex` is the explicit version of the implicit read-model refresh that query
commands already perform. It is useful after manual file edits, manual
`topics.yaml` edits, schema resets, or when a user wants visible confirmation
that the derived projection has been rebuilt.

## Architecture

Cosmic Python chapter 12's CQRS pressure applies here:

- committed markdown files under `.almanac/` are the write-side truth
- `.almanac/index.db` is a derived read model
- query commands may silently ensure the projection exists
- explicit `reindex` is a command that mutates only the projection and reports
  rebuild stats

`build` stays in `workflows/build` because it coordinates workspace registry,
wiki scaffold files, and index rebuild.

`reindex` stays on the index service because the index service owns the SQLite
projection. The CLI adapts arguments to request models and renders one-line
summaries.

## Out Of Scope

- AI Build operation
- source ingest
- jobs/runs ledger
- hosted sync, login, upload, MCP, or SDK behavior
- incremental index freshness optimization

## Tests

- service-layer build test: scaffold plus index result
- CLI build test: creates wiki, index file, and one-line summary
- CLI reindex test: indexes manually written pages and prints stats
- top-level CLI help includes `build` and `reindex`
- live temp-repo build/reindex smoke
