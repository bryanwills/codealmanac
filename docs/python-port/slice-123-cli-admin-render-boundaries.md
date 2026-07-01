# Slice 123: CLI Admin Render Boundaries

## Scope

Keep admin CLI output unchanged while splitting the admin render edge by output
family.

## Out of scope

- No parser flag changes.
- No dispatch request changes.
- No service/workflow behavior changes.
- No setup Rich redesign.

## Design

Cosmic Python chapter 13 frames the bootstrap/composition root as the place
where dependencies are wired, not where behavior accumulates. The same adapter
rule applies at the CLI edge: dispatchers call services, renderers display
typed service results, and no renderer should become a catchall for unrelated
admin surfaces.

The split is:

```python
cli.render.admin       # admin-render facade only
  -> automation.py     # automation install/status/uninstall output
  -> diagnostics.py    # doctor output
  -> jobs.py           # jobs list/show/logs/attach/cancel output
  -> updates.py        # update check/run output
  -> setup.py          # setup/uninstall result output and Rich presentation
```

`cli/render/admin.py` remains import-compatible for dispatchers. New admin
output belongs in the module for the result family it displays.

## Verification

- Focused CLI, automation, setup, and architecture tests.
- Architecture guard keeping service model imports and `render_*` definitions
  out of `cli/render/admin.py`.
- Isolated public CLI dogfood for doctor, automation status, setup/uninstall
  JSON, jobs JSON/readback, and update check.
