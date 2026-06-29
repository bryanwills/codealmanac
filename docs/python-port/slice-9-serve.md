# Slice 9: Local Serve Viewer

## Scope

Add the local read-only viewer command:

```text
codealmanac serve [--host 127.0.0.1] [--port 3927] [--wiki <name>]
```

The first Python slice restores the core human browsing path: overview, page,
topic, and search views over the current local wiki. It does not restore the
archived TypeScript jobs dashboard or review inbox because `runs`, `jobs`, and
review services do not exist in the Python product yet.

## Product Semantics

`serve` is local-only. It reads the repo-owned `.almanac/` wiki and the derived
SQLite index. It does not call AI, edit pages, upload material, authenticate, or
talk to hosted services.

The server defaults to the current repo wiki, matching the rest of the Python
CLI. `--wiki <name>` targets another registered local wiki. There is no sticky
`use` state.

## Architecture

Cosmic Python chapter 4's Service Layer pressure applies directly: the HTTP
server is an entrypoint, not the owner of product orchestration. FastAPI route
handlers parse web parameters and return HTTP responses; `ViewerService` owns
overview/page/topic/search assembly.

```text
codealmanac serve
  -> cli/main.py
  -> server/app.py
  -> services/viewer/service.py
  -> services/index/service.py
```

The viewer service reuses the existing index read model. It must not open
SQLite directly or parse page markdown from files. The only page rendering
logic it owns is local browser presentation: markdown rendering and wikilink
route rewriting.

Slice-9 review found that `serve` made forced index rebuilds on ordinary reads
too expensive. The fix is recorded in `fixes-slice-9-review.md`: `ensure_fresh`
now skips SQLite writes when the source wiki signature is unchanged, while
`reindex` remains the forced rebuild command.

## Libraries

- FastAPI is the local HTTP adapter framework. It gives typed route response
  models and `TestClient`.
- Uvicorn is the ASGI runtime used by the blocking CLI command.
- markdown-it-py renders CommonMark with HTML disabled, so page HTML is escaped
  before insertion into the browser shell.

Sources checked while planning:

- https://fastapi.tiangolo.com/
- https://fastapi.tiangolo.com/tutorial/testing/
- https://www.uvicorn.org/
- https://markdown-it-py.readthedocs.io/en/latest/using.html
- https://markdown-it-py.readthedocs.io/en/latest/security.html

## Out Of Scope

- hosted viewer
- editing UI
- auth
- jobs dashboard
- review inbox
- source/file route
- suggestion API
- semantic search
- global all-wiki browser

## Tests

- service tests for overview, page rendering, search, topic, backlinks, and file
  refs
- FastAPI adapter tests for static assets, API routes, and error mapping
- CLI help smoke for `serve`
- live dogfood: start `codealmanac serve`, query API, inspect the browser UI
