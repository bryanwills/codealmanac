# Slice 49 - CLI Admin Edge Split

Date: 2026-06-29

## Scope

Split the admin command adapter out of the broad CLI dispatch/render roots.

## Decisions

- Keep `cli/main.py` as the executable entrypoint and `cli/parser/` as the
  command parser package.
- Move `doctor`, `update`, `jobs`, and `automation` dispatch to
  `cli/dispatch/admin.py`.
- Move admin output rendering to `cli/render/admin.py`.
- Move shared CLI config/duration resolution to `cli/dispatch/config.py`.
- Keep services and workflows unchanged; the CLI remains an adapter that builds
  request models and calls `CodeAlmanac`.
- Do not split wiki and lifecycle dispatch until the next concrete command
  change creates pressure.

## Cosmic Python Transfer

Cosmic Python chapter 4 frames the service layer as the use-case boundary
between entrypoints and the domain. Chapter 13 moves setup responsibility out
of entrypoints and into a composition root. This slice applies that by keeping
admin command modules as entrypoint adapters only:

```python
def dispatch(args, app):
    if is_admin_command(args.command):
        return dispatch_admin(args, app)

def dispatch_admin(args, app):
    plan = app.updates.check(CheckUpdateRequest())
    render_update_plan(plan, json_output=args.json)
```

`dispatch_admin()` does not own update, diagnostics, run, or automation product
logic. It delegates to `app.updates`, `app.diagnostics`, `app.runs`, and
`app.automation`.

## Files

- `src/codealmanac/cli/dispatch/root.py`
- `src/codealmanac/cli/dispatch/admin.py`
- `src/codealmanac/cli/dispatch/config.py`
- `src/codealmanac/cli/render/root.py`
- `src/codealmanac/cli/render/admin.py`
- `tests/test_architecture.py`

## Verification

- Focused architecture and admin CLI tests.
- Focused ruff over CLI modules and related tests.
- Live CLI dogfood for `update --check --json`, `doctor --json`,
  `automation status --json`, `jobs --json --limit 1`, and `--help`.
- Full pytest, full ruff, diff check, package build, and wheel inspection.
