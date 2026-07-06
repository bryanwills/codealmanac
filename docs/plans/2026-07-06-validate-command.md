# Validate Command Implementation Plan

**Goal:** Add `codealmanac validate` as the concrete correctness gate for agents
and lifecycle runs.

**Architecture:** Validation is a service-layer use case on the health boundary.
It composes existing index refresh, health graph checks, raw source-shape
checks, and runtime-leak checks into one verdict. CLI parsing and rendering stay
thin. Lifecycle workflows call the same validator before marking a page-writing
run done.

Cosmic Python service-layer rule applied here: use cases live behind service
methods so CLI and workflows do not reach into stores or parse persistence
state directly. See `docs/reference/cosmic-python/chapter_04_service_layer.md`.

## Validation Shape

```python
result = app.health.validate(ValidateWikiRequest(cwd=Path.cwd(), wiki=args.wiki))
render_validate(result, json_output=args.json)
return 0 if result.ok else 1
```

The service result carries:

- selected workspace name and `almanac/` path,
- index refresh evidence,
- structured validation issues,
- `ok` boolean.

## Checks

### Page And Index Checks

- Refresh the derived index from the current Markdown tree.
- Treat route-collision failures as validation issues instead of tracebacks.
- Use existing health views for broken Markdown page links, dead file sources,
  empty topics, empty pages, orphan pages, duplicate sources, unused sources,
  and missing source citations.

### Source Shape Checks

- Walk current page Markdown files under `almanac/`.
- Inspect raw `sources:` frontmatter.
- Report invalid source lists, invalid source entries, unsupported source
  types, missing source ids, and missing source targets.
- Keep the parser contract in one place by reusing the existing source parser
  where possible.

### Runtime Leak Checks

- Report repo-local runtime files under `almanac/`:
  - `index.db`
  - `index.db-wal`
  - `index.db-shm`
  - `jobs/`
  - `runs/`

Runtime state belongs under `~/.codealmanac/repos/<workspace-id>/`.

### Lifecycle Hook

- After a harness mutates `almanac/` and mutation safety passes, refresh the
  index and run validation.
- If validation fails, fail the run before terminal `done`.
- Test harness fixtures should cite declared sources instead of weakening
  validation.

## Files

- `src/codealmanac/services/health/models.py`
- `src/codealmanac/services/health/requests.py`
- `src/codealmanac/services/health/service.py`
- `src/codealmanac/services/health/sources.py`
- `src/codealmanac/services/health/runtime.py`
- `src/codealmanac/cli/parser/wiki.py`
- `src/codealmanac/cli/dispatch/wiki.py`
- `src/codealmanac/cli/render/health.py`
- `src/codealmanac/workflows/page_run/service.py`
- `src/codealmanac/app.py`
- `tests/test_validate.py`
- affected lifecycle/CLI harness fixtures

## Verification

```bash
uv run pytest tests/test_validate.py tests/test_topics_health.py tests/test_ingest_workflow.py tests/test_garden_workflow.py tests/test_run_queue_workflow.py tests/test_cli.py
uv run pytest
uv run ruff check .
tmp_home=$(mktemp -d)
HOME="$tmp_home" uv run codealmanac validate
```

Expected:

- good starter wiki validates cleanly,
- broken Markdown links fail validation,
- route collisions fail validation without traceback,
- invalid `sources:` shape fails validation,
- runtime files under `almanac/` fail validation,
- lifecycle runs fail before `done` when they leave validation issues,
- CLI returns `0` for clean and `1` for validation issues.
