# Slice 124: CLI Admin Dispatch Boundaries

## Scope

Keep admin CLI behavior unchanged while splitting the admin dispatch edge by
command family.

## Out of scope

- No parser flag changes.
- No render output changes.
- No service/workflow behavior changes.
- No setup interaction redesign.

## Design

Cosmic Python chapter 13 keeps dependency wiring explicit at the composition
root, and chapter 4 keeps entrypoint code separate from use-case behavior. The
admin dispatch edge should adapt parsed arguments into service request models.
It should not keep every admin command, helper parser, setup automation rule,
and jobs subcommand in one file.

The split is:

```python
cli.dispatch.admin       # admin-command facade only
  -> setup.py            # setup/uninstall request construction
  -> diagnostics.py      # doctor request construction
  -> updates.py          # update request construction
  -> jobs.py             # jobs request construction
  -> automation.py       # automation request construction
```

`cli/dispatch/admin.py` remains import-compatible for the root dispatcher. New
admin command behavior belongs in the command-family dispatcher that constructs
the relevant service request.

## Verification

- Focused CLI, automation, setup, and architecture tests.
- Architecture guard keeping service request imports and command-family helpers
  out of `cli/dispatch/admin.py`.
- Isolated public CLI dogfood for doctor, update check, setup/uninstall JSON,
  automation status, and jobs readback.
