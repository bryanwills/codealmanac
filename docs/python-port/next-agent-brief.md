# Next Agent Brief

Updated: 2026-06-29

## Current State

- Goal is active: rebuild CodeAlmanac from scratch as a Python codebase.
- Branch: `codex/python-port-archive-existing-code`.
- The old TypeScript code is staged under `archive/code/`.
- `docs/python-port-live-agreement.md` is the live contract.
- `docs/reference/cosmic-python/` contains Markdown-only reference chapters.
- Steering docs live in `docs/python-port/`.

## Last Good Evidence

- `MANUAL.md`, `CLAUDE.md`, `.almanac/README.md`, the live agreement, and the
  Cosmic Python guide were read on 2026-06-29.
- The relevant Cosmic Python pressure for the first slice is:
  - code under `src`
  - entrypoints thin
  - service-layer tests where possible
  - dependencies wired in one composition root

## Dirty/Staged Files

At this checkpoint, the archive/docs baseline is staged and should be committed
before starting Python code if `git diff --cached --check` passes.

## Next Move

1. Verify and commit the archive/docs/steering baseline.
2. Scaffold `pyproject.toml`, `src/codealmanac/`, and `tests/`.
3. Implement the minimal composition root, CLI, and workspace init service.
4. Add pytest coverage and run a live `codealmanac init` smoke test.

## Things Not To Do

- Do not resurrect public `almanac`, `alm`, `absorb`, or `capture` commands.
- Do not make CLI commands the internal API.
- Do not pull hosted product assumptions into local v1.
- Do not copy the TypeScript structure just because it exists in `archive/code/`.
