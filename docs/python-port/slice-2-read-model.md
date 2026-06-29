# Slice 2: SQLite Read Model

Date: 2026-06-29

## Scope

Build the local read path for repo-owned `.almanac/` pages:

- parse markdown pages and YAML frontmatter
- classify `[[...]]` links into page, file, folder, and cross-wiki refs
- maintain `.almanac/index.db` with SQLite + FTS5
- implicitly refresh the index before read commands
- add `codealmanac search` and `codealmanac show`

## Out Of Scope

- no hosted commands or remote sync
- no AI lifecycle work
- no `ingest`, `sync`, `garden`, `jobs`, `health`, or `topics` command
- no semantic/vector search
- no compatibility aliases

## Architecture

```python
app.index.ensure_fresh(workspace_id)
app.search.search(workspace_id, SearchPagesRequest(...))
app.pages.show(workspace_id, ShowPageRequest(...))
```

`wiki` owns markdown parsing, frontmatter, path normalization, and wikilink
classification. `index` owns SQLite schema, freshness, FTS, and read queries.
CLI resolves the workspace and renders service results.

This follows the Cosmic Python repository pressure without adding a Unit of
Work yet. There is one durable store in this slice, and each operation is a
single SQLite transaction.

## Files

- `src/codealmanac/services/wiki/`: page parser, wikilinks, page models
- `src/codealmanac/services/index/`: schema, store, service, requests
- `src/codealmanac/services/search/`: search request/result service
- `src/codealmanac/services/pages/`: show request/result service
- `src/codealmanac/cli/main.py`: `search` and `show` adapters
- `tests/`: parser, index/search, show, and CLI tests

## Compatibility To Preserve

- commands run inside a repo resolve the nearest `.almanac/`
- `--wiki <name>` selects another registered local wiki
- `search` prints slugs by default
- empty search prints no stdout and `# 0 results` to stderr
- `show <slug>` prints body by default
- `show --meta`, `--body`, `--lead`, `--links`, `--backlinks`, `--files`,
  `--topics`, and `--json` are read-only views
- `--mentions` uses normalized paths and SQLite `GLOB`, not `LIKE`

## Verification

- `uv run pytest`
- `uv run ruff check .`
- live temp repo:
  - `codealmanac init`
  - create pages with topics, file refs, links
  - `codealmanac search`
  - `codealmanac search --mentions`
  - `codealmanac show`
