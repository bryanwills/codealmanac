# Next Agent Brief

Updated: 2026-06-29

## Current State

- Goal is active: rebuild CodeAlmanac from scratch as a Python codebase.
- Branch: `codex/python-port-archive-existing-code`.
- Archive/docs baseline committed as `4520812`.
- First Python scaffold committed as `a803f63`.
- `docs/python-port-live-agreement.md` is the live contract.
- `docs/reference/cosmic-python/` contains Markdown-only reference chapters.
- Steering docs live in `docs/python-port/`.
- First Python scaffold exists under `src/codealmanac/` with CLI, app,
  workspaces, wiki scaffold, and build workflow.

## Last Good Evidence

- `MANUAL.md`, `CLAUDE.md`, `.almanac/README.md`, the live agreement, and the
  Cosmic Python guide were read on 2026-06-29.
- The relevant Cosmic Python pressure for the first slice is:
  - code under `src`
  - entrypoints thin
  - service-layer tests where possible
  - dependencies wired in one composition root
- First scaffold verification passed:
  - `uv run pytest`
  - `uv run ruff check .`
  - `uv run codealmanac --help`
  - isolated live `codealmanac init` and `codealmanac list`
- Slice-1 review fix hardened workspace registry temp writes and passed:
  - `uv run pytest`
  - `uv run ruff check .`
  - isolated live `codealmanac init` and `codealmanac list`

## Dirty/Staged Files

At this checkpoint, only the slice-1 review fix should be dirty until it is
committed. Re-run `git diff --check`, `uv run pytest`, `uv run ruff check .`,
and the live CLI smoke before committing.

## Next Move

1. Commit the slice-1 review fix if it is still unstaged/uncommitted.
2. Start the SQLite read-model slice: `database/`, `wiki` page parsing,
   `index` service, and `search`/`show` commands.
3. Add focused service/store tests before broad CLI tests.
4. Add an architecture test that CLI imports do not import concrete integration
   modules once integrations exist.

## Things Not To Do

- Do not resurrect public `almanac`, `alm`, `absorb`, or `capture` commands.
- Do not make CLI commands the internal API.
- Do not pull hosted product assumptions into local v1.
- Do not copy the TypeScript structure just because it exists in `archive/code/`.
