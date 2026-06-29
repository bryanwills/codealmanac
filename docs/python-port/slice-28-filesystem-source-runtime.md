# Slice 28 - Filesystem Source Runtime

Date: 2026-06-29

## Scope

Add bounded readable runtime material for local path source refs:

- `SourceKind.PATH_FILE`
- `SourceKind.PATH_DIRECTORY`
- `SourceKind.PATH_UNKNOWN`

This slice makes ordinary inputs such as `codealmanac ingest notes.md` and
`codealmanac ingest src/` actually carry local file material into the Ingest
prompt. It does not add a durable source catalog, a new CLI verb, semantic
search, file watching, hosted upload, or a general repository crawler.

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `docs/python-port-live-agreement.md`
- `docs/reference/cosmic-python/CODEALMANAC.md`
- `docs/reference/cosmic-python/chapter_02_repository.md`
- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_13_dependency_injection.md`
- `pathspec` docs for gitignore-style pattern matching
- `charset-normalizer` docs for decoding bytes into text

## Design

The source service already classifies path inputs and fingerprints files. That
is not enough for Ingest: the writer needs the file text or a bounded directory
context before it can decide whether wiki knowledge changed.

```python
brief = app.sources.resolve(... "notes.md" ...)
runtime = app.sources.inspect_runtime(InspectSourceRuntimeRequest(ref=brief.ref))
prompt = render_ingest_prompt(..., source_runtime=(runtime,))
```

The new concrete adapter lives at `integrations/sources/filesystem/adapter.py`
and implements `SourceRuntimeAdapter`.

The adapter:

- supports local file, directory, and missing-path refs
- reads text files with bounded bytes
- decodes bytes through `charset-normalizer`
- returns `unavailable` for missing paths and unreadable binary files
- walks directories lazily and stops after a file-count bound
- respects a root `.gitignore` through `pathspec`
- skips known generated/private directories during directory traversal
- renders directory runtime as metadata, a compact tree, and included file
  sections

Explicit file inputs still read the named file. Directory traversal filters
`.git/`, `.almanac/`, `node_modules/`, virtualenv/cache directories,
`.gitignore`, and local `.env` files because those are not useful source
material for wiki updates and may leak implementation noise or secrets.

## Tests

- New `tests/test_filesystem_source_runtime.py`
  - text file content reaches runtime
  - missing paths are unavailable
  - binary files are unavailable
  - directory traversal respects `.gitignore` and default skips
  - directory file count is bounded
  - large file bytes are bounded
- Existing `tests/test_ingest_workflow.py`
  - ordinary `note.md` ingest now receives available file runtime content
    instead of a skipped runtime snapshot
- Architecture test stays green
  - services/workflows/CLI still do not import concrete integrations

## Verification Plan

Focused:

```bash
uv run pytest tests/test_filesystem_source_runtime.py tests/test_sources_service.py tests/test_ingest_workflow.py tests/test_architecture.py
uv run ruff check src/codealmanac/integrations/sources tests/test_filesystem_source_runtime.py tests/test_ingest_workflow.py
```

Full:

```bash
uv run pytest
uv run ruff check src tests
git diff --check
uv build --out-dir /tmp/codealmanac-build-slice28
```

Dogfood:

- temp Git repo
- real default `FilesystemSourceRuntimeAdapter`
- local `notes.md` and `src/` inputs
- fake harness that writes one wiki page
- assert the prompt contains local file and directory content and search finds
  the written page
