# Slice 121: CLI Wiki Dispatch Boundaries

## Scope

Keep wiki CLI behavior unchanged while splitting the wiki dispatch edge by
command family.

## Out of scope

- No parser flag changes.
- No render output changes.
- No service/workflow behavior changes.
- No hosted command surface.

## Design

Cosmic Python chapter 4 separates interfacing code from service-layer use
cases, and chapter 13 keeps entrypoint composition explicit. The CLI dispatch
edge should translate parsed arguments into service request objects and then
delegate to renderers. It should not accumulate every wiki-adjacent subcommand
in one file.

The current `../almanac` CLI keeps command-family dispatchers small. CodeAlmanac
should keep the same feel:

```python
if args.command == "list":
    return dispatch_workspaces(args, app)
if args.command == "topics":
    return dispatch_topics(args, app)
if args.command == "serve":
    return run_serve(app, args)
```

`dispatch/wiki.py` remains the wiki-command facade for search/show/health/
reindex/tag/untag routing. `dispatch/topics.py` owns topic subcommands.
`dispatch/workspaces.py` owns `list`/drop/drop-missing. `dispatch/serve.py`
owns local viewer startup.

## Verification

- Focused CLI and topic mutation tests.
- Architecture guard keeping topic/workspace request construction and uvicorn
  startup out of `dispatch/wiki.py`.
- Isolated public CLI dogfood for list, search, show, topics, and serve.
