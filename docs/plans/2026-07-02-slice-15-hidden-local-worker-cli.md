# Slice 15 Plan: Hidden Local Worker CLI

Status: planned.
Date: 2026-07-02.

## Intent

Expose the new local worker workflow through an internal CLI command:

```bash
codealmanac __run-local-worker --using codex --json
```

This gives hooks, future background spawners, tests, and operators one stable
entry point without making it part of the public launch CLI yet.

## Product Contract

- The command is hidden from help.
- The command calls `app.workflows.local_worker.run_next(...)`.
- The command processes at most one pending trigger.
- The command can filter by `repository_id` and `branch_id`.
- The command defaults to quiet output.
- `--json` prints the typed workflow result for debugging and tests.
- Normal no-op and run-failed outcomes still exit `0`; the run state is in the
  control DB.

## Code Shape

```python
if args.command == "__run-local-worker":
    result = app.workflows.local_worker.run_next(
        RunNextLocalWorkerRequest(
            repository_id=args.repository_id,
            branch_id=args.branch_id,
            operation=args.operation,
            harness=HarnessKind(args.using),
            title=args.title,
        )
    )
```

## Implementation Scope

Add:

- hidden parser entry `__run-local-worker`
- dispatch module `cli/dispatch/local_worker.py`
- lifecycle dispatch wiring
- CLI tests for no-op JSON and successful one-trigger processing

Out of scope:

- changing Git hook blocks
- background process spawning
- public `local` command surface
- cloud worker command

## Verification

Focused:

```bash
uv run pytest tests/test_cli.py tests/test_local_worker_workflow.py tests/test_architecture.py
```

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
