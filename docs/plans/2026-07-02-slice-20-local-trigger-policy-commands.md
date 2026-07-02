# Slice 20 Plan: Local Trigger Policy Commands

Status: implemented.
Date: 2026-07-02.

## Intent

Add the public local configuration commands that complete the setup/update/jobs
surface:

```bash
codealmanac local triggers list
codealmanac local triggers enable <branch> [--delivery commit|working-tree]
codealmanac local triggers disable <branch>
codealmanac local delivery set --branch <branch> --mode commit|working-tree
```

These commands let a local user configure which branches are maintained and how
local updates are delivered without reinstalling hooks or running an update.

## Product Contract

- Commands are scoped to the current Git checkout's configured local repository.
- The repository must already be registered by `codealmanac local setup`.
- `triggers list` lists configured branch policy rows for the current repo.
- `triggers enable <branch>` enables that branch. If `--delivery` is omitted,
  it preserves the existing delivery mode or defaults to `commit`.
- `triggers disable <branch>` disables that branch and preserves the existing
  delivery mode when a branch row already exists.
- `delivery set --branch <branch> --mode ...` only changes delivery mode. It
  requires an existing branch policy row and does not enable or disable the
  trigger.
- These commands mutate `~/.codealmanac/control.sqlite`; they do not install Git
  hooks, spawn workers, or run model work.

## Code Shape

Add a control read:

```python
branches = control.list_branches(ListBranchesRequest(repository_id=repo.id))
```

Add a local policy workflow:

```python
result = app.workflows.local_policy.enable_trigger(
    UpdateLocalTriggerPolicyRequest(
        cwd=Path.cwd(),
        branch_name=args.branch,
        delivery_mode=parse_optional_delivery(args.delivery),
    )
)
```

The workflow uses `local_status` to resolve the current configured repository,
then calls `control.find_branch_by_name`, `control.list_branches`, or
`control.set_branch_policy`. CLI dispatch remains a thin mapper.

## Implementation Scope

Add:

- `ListBranchesRequest` on the control service.
- `ControlStore.list_branches(...)` ordered by branch name.
- `workflows/local_policy/` with typed requests and result models.
- CLI parsers/dispatch/rendering for `local triggers` and `local delivery`.
- focused control, workflow, CLI, and architecture tests.

Out of scope:

- cloud trigger policy commands.
- local schedule/time automation.
- hook installation repair.
- running a local update after policy changes.
- reading remote Git branch lists.

## Verification

Focused:

```bash
uv run pytest tests/test_control_service.py tests/test_local_policy_workflow.py tests/test_cli.py tests/test_architecture.py
```

Result: `137 passed`.

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
```

Result: `456 passed`; ruff and diff-check passed.
