# Slice 93: Retire Generic Services Package

## Goal

Remove the remaining active `src/codealmanac/services/` package. The package
now groups unrelated concepts only because they used to be implemented before
the cloud/local/wiki/engine split. The active package tree should tell a new
agent where a concept belongs without requiring search.

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `/Users/rohan/.codex/skills/slow-development/SKILL.md`
- `/Users/rohan/.codex/skills/python-code-quality/SKILL.md`
- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_13_dependency_injection.md`

The relevant Cosmic Python pressure is: entrypoints should call a service
layer, and the composition root owns dependency wiring. This slice preserves
`app.py` as the composition root while making the service package names carry
real domain ownership.

## New Package Ownership

```text
src/codealmanac/config/                 # product config models/store/service
src/codealmanac/diagnostics/            # doctor checks and report assembly
src/codealmanac/cloud/setup/            # cloud-first root setup workflow
src/codealmanac/wiki/tagging/           # deterministic wiki metadata edits
src/codealmanac/maintenance/updates/    # package update/self-update checks
```

## Scope

- Move the five remaining service subpackages into those owners.
- Update all active imports in `src/` and `tests/`.
- Update package data so `agent-guide.md` ships from `codealmanac.cloud.setup`.
- Update architecture guards that intentionally name these packages.
- Add a guard that prevents active source/tests from reintroducing
  `codealmanac.services` imports or `src/codealmanac/services/`.
- Update launch progress/worklog/next-agent notes after verification.

## Out Of Scope

- No public CLI behavior changes.
- No hosted repo changes.
- No historical doc rewrites except launch status files that describe the
  current architecture.
- No PyPI release unless behavior or packaging verification reveals a release
  need.

## Verification

- Focused tests for config, diagnostics, setup, tagging, updates, CLI, and the
  updated architecture guards.
- Full `uv run pytest -q`.
- `uv run ruff check src tests`.
- `uv run ruff format --check src tests`.
- `uv run python -m compileall src -q`.
- Build wheel and verify `agent-guide.md` is packaged under
  `codealmanac/cloud/setup/`, with no `codealmanac/services/` package files.
- `git diff --check`.
