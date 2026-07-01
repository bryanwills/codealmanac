# Slice 126: CLI Admin Parser Boundaries

## Scope

Keep admin CLI flags unchanged while splitting the admin parser edge by command
family.

## Out of scope

- No flag names, defaults, or help text changes.
- No dispatch/render changes.
- No service/workflow behavior changes.

## Design

Cosmic Python chapter 4 separates interfacing code from service-layer use cases.
The parser is pure interfacing code, but it still has reasons to change by
command family. Setup/uninstall, doctor, update, jobs, and automation flags
should not all live in one admin parser file when dispatch and render already
have command-family boundaries.

The split is:

```python
cli.parser.admin        # admin-parser facade only
  -> setup.py           # setup/uninstall flags
  -> diagnostics.py     # doctor flags
  -> updates.py         # update flags
  -> jobs.py            # jobs flags
  -> automation.py      # automation flags and task choices
```

`cli/parser/admin.py` remains import-compatible for the root parser. New admin
flags belong in the command-family parser that owns the command surface.

## Verification

- Focused parser/public-contract/CLI architecture tests.
- Architecture guard keeping `add_parser(...)` command construction out of
  `cli/parser/admin.py`.
- Public help dogfood for setup, uninstall, doctor, update, jobs, and
  automation.
