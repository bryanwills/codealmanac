# Slice 17 Plan: Local Setup Command

Status: planned.
Date: 2026-07-02.

## Intent

Add the first public launch-shaped local setup command:

```bash
codealmanac local setup --delivery commit
codealmanac local setup --delivery working-tree
```

This command registers the current GitHub checkout in the local control DB,
enables trigger policy for a branch, and installs local Git hook blocks.

## Product Contract

- `codealmanac local setup` is explicit local setup.
- It does not run a wiki update.
- It detects the current Git checkout and GitHub remote.
- It stores repository and branch policy in `~/.codealmanac/control.sqlite`.
- It installs local Git hook blocks unless `--skip-hooks` is passed.
- Delivery mode is branch-scoped.
- Supported local delivery modes are `commit` and `working-tree`.

## Code Shape

```python
result = app.workflows.local_setup.setup(
    RunLocalSetupRequest(
        cwd=Path.cwd(),
        branch_name=args.branch,
        almanac_root=Path(args.root),
        delivery_mode=ControlDeliveryMode(args.delivery),
        install_hooks=not args.skip_hooks,
    )
)
```

Ownership:

- `workflows/local_setup/` owns local setup orchestration.
- A service-owned `LocalRepositoryProbe` port describes Git checkout and remote
  identity.
- Git remote parsing lives in `integrations/workspaces/git/`.
- `local_hooks` remains the only owner of hook file writes.
- `control` remains the only owner of repository/branch SQL.

## Implementation Scope

Add:

- `workflows/local_setup/` package with models, requests, ports, and service.
- `GitLocalRepositoryProbe` integration.
- `codealmanac local setup` parser and dispatch.
- JSON and compact text render output.
- local `working-tree` delivery support so setup does not expose an unsupported
  delivery mode.
- focused workflow, CLI, Git probe, and delivery tests.

Out of scope:

- cloud `codealmanac setup`
- public `local update`
- repo trigger list/status commands
- capture setup
- cloud API/auth work

## Verification

Focused:

```bash
uv run pytest tests/test_local_setup_workflow.py tests/test_cli.py tests/test_git_local_repository_probe.py tests/test_local_delivery_workflow.py tests/test_git_local_delivery.py tests/test_architecture.py
```

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
