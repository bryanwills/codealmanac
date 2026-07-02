# Slice 23 Dev Lifecycle CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove `ingest` and `garden` from the normal public top-level CLI
surface while keeping explicit developer access to the existing lifecycle
workflows.

**Architecture:** Keep the workflow and render layers unchanged. Move the human
CLI entrypoints for manual ingest and garden under a hidden `dev` command group
that reuses the same dispatch functions, so the launch-facing help matches the
cloud/local contract without deleting internal lifecycle machinery.

**Tech Stack:** Python, argparse, thin CLI parser/dispatch modules, existing
Pydantic workflow requests, pytest.

**Status:** Implemented on 2026-07-02.

---

## Scope

- Top-level `codealmanac --help` no longer lists `ingest` or `garden`.
- Top-level `codealmanac ingest ...` and `codealmanac garden ...` are removed
  from the public parser.
- Hidden developer commands exist:
  - `codealmanac dev ingest <inputs...>`
  - `codealmanac dev garden`
- `dev ingest` and `dev garden` preserve the existing flags and behavior:
  `--wiki`, `--using`, `--title`, `--guidance`, `--background`,
  `--foreground`, and `--json`.
- Existing workflow code, prompts, queue specs, automation internals, and run
  records remain unchanged.
- Launch docs describe `dev ingest` and `dev garden` as non-public maintenance
  entrypoints.

## Out Of Scope

- Renaming the underlying operations or run operation enum values.
- Removing ingest/garden prompts.
- Changing scheduled sync or automation behavior.
- Cloud setup/API work.
- Local control DB/run-storage changes.

## Design

```python
# public help teaches launch commands
codealmanac init
codealmanac local ...
codealmanac sync
codealmanac serve

# hidden developer surface keeps old manual lifecycle verbs reachable
codealmanac dev ingest note.md --using codex --foreground
codealmanac dev garden --using codex --background

# dispatch stays thin
dispatch_dev(args, app)
  if args.dev_command == "ingest": return dispatch_ingest(args, app)
  if args.dev_command == "garden": return dispatch_garden(args, app)
```

`dev` is hidden from normal top-level help because the launch CLI should not
teach maintainers-only lifecycle commands. It is still an intentional command
namespace, not an underscore-only private hook, so agents and maintainers can
invoke it clearly when needed.

## Files

Create:

- `src/codealmanac/cli/parser/dev.py`
- `src/codealmanac/cli/dispatch/dev.py`

Modify:

- `src/codealmanac/cli/parser/root.py`
- `src/codealmanac/cli/parser/lifecycle.py`
- `src/codealmanac/cli/dispatch/root.py`
- `src/codealmanac/cli/dispatch/lifecycle.py`
- `tests/test_cli.py`
- `tests/test_architecture.py`, only if the new parser/dispatch modules need
  explicit architecture coverage
- `docs/codealmanac-launch/cli-contract.md`
- `docs/codealmanac-launch/progress.md`
- `docs/codealmanac-launch/worklog.md`
- `docs/codealmanac-launch/verification-matrix.md`
- `docs/codealmanac-launch/next-agent-brief.md`

## Tests

Focused:

```bash
uv run pytest tests/test_cli.py tests/test_architecture.py
```

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
uv run codealmanac --help
uv run codealmanac dev ingest --help
uv run codealmanac dev garden --help
```

## Implementation Tasks

1. Add hidden `dev` parser commands for `ingest` and `garden`.
2. Add `dev` dispatch that reuses `dispatch_ingest` and `dispatch_garden`.
3. Remove public top-level `ingest` and `garden` parser/dispatch registration.
4. Update CLI tests to assert public help hides `ingest`, `garden`, and `dev`.
5. Move existing CLI lifecycle behavior tests from top-level commands to
   `dev ingest` and `dev garden`.
6. Run focused tests and fix parser/dispatch issues.
7. Update launch docs with the finalized hidden-dev command contract.
8. Run the full verification gate.
9. Commit, push, send RelayForge, and record the relay/bookkeeping update.

## Verification Performed

```bash
uv run pytest tests/test_cli.py tests/test_architecture.py
# 113 passed

uv run pytest tests/test_public_contract.py tests/test_cli.py tests/test_architecture.py
# 140 passed

uv run pytest
# 466 passed

uv run ruff check .
git diff --check
uv run codealmanac --help
uv run codealmanac dev ingest --help
uv run codealmanac dev garden --help
```
