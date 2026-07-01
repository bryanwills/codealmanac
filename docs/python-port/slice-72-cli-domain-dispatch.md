# Slice 72 - CLI Domain Dispatch

Date: 2026-07-01

## Scope

Split the remaining broad CLI dispatch root into domain dispatch modules without
changing the public command surface.

This is an architecture slice, not a feature slice. It prepares the CLI edge for
background jobs, richer harness flows, setup/uninstall, and page sources by
making command ownership visible before those commands grow.

## Decisions

- Keep `argparse` and the existing command names.
- Keep `cli/main.py` as the process entrypoint.
- Keep parser modules unchanged unless tests expose a mismatch.
- Move lifecycle commands to `cli/dispatch/lifecycle.py`.
- Move read/wiki organization commands to `cli/dispatch/wiki.py`.
- Keep admin commands in `cli/dispatch/admin.py`.
- Keep `cli/dispatch/root.py` as a small delegator only.
- Keep services and workflows unchanged; CLI dispatch remains an adapter that
  builds request models and calls the app composition root.

## Cosmic Python Transfer

Chapter 4 describes the service layer as the place that defines the system's
use cases. This slice keeps CLI modules from becoming a second service layer:

```python
def dispatch(args, app):
    if is_lifecycle_command(args.command):
        return dispatch_lifecycle(args, app)
    if is_wiki_command(args.command):
        return dispatch_wiki(args, app)
    if is_admin_command(args.command):
        return dispatch_admin(args, app)
```

Chapter 13 moves setup work out of entrypoints and into a composition root. This
slice preserves that direction by keeping concrete services on `CodeAlmanac`
and not constructing product dependencies inside command handlers.

## Files

- `src/codealmanac/cli/dispatch/root.py`
- `src/codealmanac/cli/dispatch/lifecycle.py`
- `src/codealmanac/cli/dispatch/wiki.py`
- `tests/test_architecture.py`
- `tests/test_cli.py`

## Verification

Run focused checks first:

```bash
uv run pytest tests/test_architecture.py tests/test_cli.py tests/test_public_contract.py
uv run ruff check src/codealmanac/cli tests/test_architecture.py tests/test_cli.py tests/test_public_contract.py
```

Run broader checks if the split touches behavior outside command dispatch:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
