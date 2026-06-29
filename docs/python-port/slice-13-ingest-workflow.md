# Slice 13: Internal Ingest Workflow

## Scope

Add the first internal `ingest` workflow:

```python
app.workflows.ingest.run(
    RunIngestRequest(
        cwd=repo,
        inputs=("note.md", "github:pr:42"),
        harness=HarnessKind.CODEX,
    )
)
```

This slice still does not expose public `codealmanac ingest`. The workflow can
execute only when a harness adapter is supplied through `create_app(...)`, so a
public command would be a runnable-looking surface over missing concrete
Codex/Claude machinery.

## Architecture

The workflow coordinates existing service-owned contracts:

```text
RunIngestRequest
  -> RunsService.start(...)
  -> SourcesService.resolve(...)
  -> HarnessesService.run(...)
  -> validate changed files stay under .almanac/
  -> IndexService.ensure_fresh(...)
  -> RunsService.finish(...)
```

Cosmic Python chapter 10 distinguishes commands from events. `RunIngestRequest`
is a command: callers expect either a completed result or a raised error. Run
log entries are events: they record facts such as "resolved 1 source" or
"codex succeeded."

The composition root now exposes workflows through `app.workflows.*`, matching
the live agreement's app-surface shape.

## Prompt Payload

The ingest prompt includes a structured Pydantic payload with workspace paths,
source briefs, and optional guidance. It uses `model_dump_json(indent=2)` rather
than manual JSON string assembly.

References:

- https://docs.pydantic.dev/latest/concepts/serialization/
- https://docs.python.org/3.12/library/pathlib.html#pathlib.PurePath.relative_to

## Safety

Harness results are accepted only when `HarnessRunStatus.SUCCEEDED` is returned.
Every reported changed file must resolve under the selected workspace's
`.almanac/` directory. If a harness reports an application-code path, the
workflow marks the run failed and raises `ValidationFailed`.

## Tests

- success path resolves sources, runs a fake harness, writes a page, refreshes
  the index, and records run events
- missing harness adapter marks the run failed and raises `NotFoundError`
- harness changes outside `.almanac/` mark the run failed and raise
  `ValidationFailed`
- failed harness status marks the run failed and raises `ExecutionFailed`
- empty input validation

## Remaining Risk

The workflow uses a fake adapter in tests. The next machinery slice needs a real
Codex or Claude integration behind `HarnessAdapter` before exposing
`codealmanac ingest`.
