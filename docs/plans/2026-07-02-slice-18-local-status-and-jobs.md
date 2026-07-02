# Slice 18 Plan: Local Status And Jobs

Status: planned.
Date: 2026-07-02.

## Intent

Add the public read surface for local setup and local run history:

```bash
codealmanac local status
codealmanac local jobs list
codealmanac local jobs show <run-id>
codealmanac local jobs logs <run-id>
```

This slice lets a human or agent verify what `local setup` configured and
inspect SQL-backed local jobs without reaching into
`~/.codealmanac/control.sqlite`.

## Product Contract

- `local status` is read-only.
- `local status` detects the current GitHub checkout, then reports whether the
  checkout and current branch are configured in the local control DB.
- `local jobs` reads the control DB run ledger, not repo-local
  `almanac/jobs/` files.
- Local job commands support JSON output for agents and compact text output for
  humans.
- This slice does not start a run. `local update` is intentionally deferred so
  manual-trigger semantics can be designed cleanly.

## Code Shape

```python
status = app.workflows.local_status.status(
    ReadLocalStatusRequest(cwd=Path.cwd())
)

runs = app.control.list_runs(
    ListControlRunsRequest(repository_id=..., branch_id=...)
)

events = app.control.list_run_events(
    ListControlRunEventsRequest(run_id=run_id)
)
```

Ownership:

- `workflows/local_status/` owns local status composition.
- `control` owns repository, branch, run, and run-event queries.
- `LocalRepositoryProbe` remains the Git checkout detection port.
- `cli/dispatch/local.py` maps CLI args to requests and renders output.
- No CLI command imports SQL, Git subprocess mechanics, or worker internals.

## Implementation Scope

Add:

- Optional control reads:
  - repository by local root
  - branch by repository/name
  - list control runs
- `workflows/local_status/` package with models, requests, and service.
- `codealmanac local status`.
- `codealmanac local jobs list|show|logs`.
- focused workflow, control, CLI, and architecture tests.

Out of scope:

- `codealmanac local update`
- hook status inspection
- cloud `runs` commands
- migration from repo-local `almanac/jobs/`
- public `ingest`/`garden` hiding

## Verification

Focused:

```bash
uv run pytest tests/test_control_service.py tests/test_local_status_workflow.py tests/test_cli.py tests/test_architecture.py
```

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
