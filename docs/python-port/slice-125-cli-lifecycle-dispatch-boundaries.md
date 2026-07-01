# Slice 125: CLI Lifecycle Dispatch Boundaries

## Scope

Keep lifecycle CLI behavior unchanged while splitting the lifecycle dispatch
edge by command family.

## Out of scope

- No parser flag changes.
- No render output changes.
- No workflow/service behavior changes.
- No background-job policy changes.

## Design

Cosmic Python chapter 4 separates interfacing code from use-case orchestration:
entrypoints adapt external input, while services/workflows own product verbs.
`cli/dispatch/lifecycle.py` had become a mixed adapter for workspace
initialization, page-writing operations, hidden worker draining, and sync
policy flags. Those command families change for different reasons.

The split is:

```python
cli.dispatch.lifecycle   # lifecycle-command facade only
  -> build.py            # init/build request construction
  -> operations.py       # ingest/garden foreground/background dispatch
  -> sync.py             # sync and sync status request construction
  -> worker.py           # hidden queue-drain entrypoint
```

`cli/dispatch/lifecycle.py` remains import-compatible for the root dispatcher.
New lifecycle command behavior belongs in the command-family dispatcher that
constructs the relevant workflow request.

## Verification

- Focused CLI, sync, ingest/garden, and architecture tests.
- Architecture guard keeping workflow request imports and sync helpers out of
  `cli/dispatch/lifecycle.py`.
- Isolated public CLI dogfood for init, build, ingest/garden background JSON,
  sync status JSON, sync background JSON, and hidden worker drain.
