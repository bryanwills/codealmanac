# Next Agent Brief

Updated: 2026-06-29

## Current State

- Goal remains active: rebuild CodeAlmanac from scratch as a Python codebase.
- Branch: `codex/python-port-archive-existing-code`.
- Last committed slice before current work: `c696361 feat(slice-26): add transcript source runtime`.
- Live contract: `docs/python-port-live-agreement.md`.
- Cosmic Python local guide: `docs/reference/cosmic-python/CODEALMANAC.md`.
- Current Python product surface includes CLI/app composition, workspace
  registry, `.almanac/` build, SQLite read model, search/show/topics/health,
  tag/untag/topic mutation, reindex, doctor, serve, runs/jobs, ingest, garden,
  foreground sync, sync status, local automation, Codex/Claude harness adapters,
  transcript discovery, and source runtime adapters.
- Source runtime now covers Git, GitHub, transcripts, and web URLs behind
  `services/sources/ports.py::SourceRuntimeAdapter`.
- Ingest remains source-kind agnostic. It resolves `SourceBrief` values, asks
  `SourcesService.inspect_runtime(...)` for snapshots, renders typed runtime
  JSON into the prompt, calls the selected harness, validates `.almanac/`
  mutation safety, refreshes the index, and records the run.
- The CLI remains a thin adapter. Do not shell out to `codealmanac` from
  workflows, automation, tests, or future server wrappers.

## Current Dirty Work

Slice 27 is implemented and verified locally but not committed yet.

Expected dirty files:

- `pyproject.toml`
- `uv.lock`
- `src/codealmanac/integrations/sources/__init__.py`
- `src/codealmanac/integrations/sources/web/__init__.py`
- `src/codealmanac/integrations/sources/web/adapter.py`
- `tests/test_web_source_runtime.py`
- `tests/test_ingest_workflow.py`
- `docs/python-port-live-agreement.md`
- `docs/python-port/slice-27-web-source-runtime.md`
- `docs/python-port/ownership-map.md`
- `docs/python-port/idea-evolution.md`
- `docs/python-port/worklog.md`
- `docs/python-port/verification-matrix.md`
- `docs/python-port/next-agent-brief.md`

## Slice 27 Summary

Added `WebSourceRuntimeAdapter` under `integrations/sources/web/`.

Behavior:

- supports `SourceKind.WEB_URL`
- fetches via `httpx`
- follows redirects
- bounds response bytes and runtime chars
- parses HTML/text-like content
- strips non-readable HTML nodes with Beautiful Soup
- returns `SourceRuntimeStatus.AVAILABLE` for readable material
- returns `SourceRuntimeStatus.UNAVAILABLE` for HTTP errors, network errors,
  missing URL refs, and unsupported binary content

Runtime dependencies added:

- `httpx>=0.28.1`
- `beautifulsoup4>=4.15.0`

## Verified

- `uv run pytest tests/test_web_source_runtime.py`
- `uv run pytest tests/test_web_source_runtime.py tests/test_sources_service.py tests/test_ingest_workflow.py tests/test_architecture.py`
- `uv run ruff check src/codealmanac/integrations/sources tests/test_web_source_runtime.py tests/test_ingest_workflow.py`
- `uv run pytest` -> 134 passed
- `uv run ruff check src tests`
- `git diff --check`
- `uv build --out-dir /tmp/codealmanac-build-slice27`
- Wheel inspection confirmed:
  - `codealmanac/integrations/sources/web/adapter.py`
  - `Requires-Dist: httpx>=0.28.1`
  - `Requires-Dist: beautifulsoup4>=4.15.0`
- Dogfood: temp Git repo, real default `WebSourceRuntimeAdapter`,
  `https://example.com/`, fake harness, `app.workflows.ingest.run(...)`, search
  readback. Runtime was `available`, prompt contained `Example Domain`, search
  found `web-runtime-dogfood`.

## Next Move

1. Re-run `git status --short`.
2. If only the expected slice-27 files are dirty, commit:
   `feat(slice-27): add web source runtime`.
3. Next implementation pressure is probably local path file/directory runtime
   through the same `SourceRuntimeAdapter` port, unless `codealmanac update` or
   viewer source/file route hardening becomes higher priority.
4. Do not add hosted CLI, login/connect/upload, MCP, SDK, public `capture`,
   public `absorb`, or public `almanac`/`alm` aliases.
5. Keep future source material additions inside `SourceAddress -> SourceRef ->
   SourceBrief -> SourceRuntime` unless the live agreement changes.
