# Slice 73 - Page Run Workflow

Date: 2026-07-01

## Scope

Extract the shared lifecycle execution used by `ingest` and `garden` into a
first-class page-run workflow without changing public behavior.

This slice is architecture cleanup. It should preserve current run event order,
failure semantics, mutation safety, prompt payloads, and CLI output.

## Why Now

`IngestWorkflow` and `GardenWorkflow` now both own the same machinery:

- mark a queued run as running
- perform the clean Almanac-root preflight
- record lifecycle messages
- call a harness
- persist normalized harness transcript and events
- validate reported and actual file mutations
- validate harness success
- refresh the index
- finish or fail the run

That duplication is already hiding the intended model. Ingest and garden are
different page-writing operations; they should not each reimplement the page-run
lifecycle.

## Decisions

- Add `codealmanac.workflows.page_run`.
- Keep operation-specific source/context/prompt preparation inside
  `IngestWorkflow` and `GardenWorkflow`.
- Move generic run/harness/safety/failure/index finalization into
  `PageRunWorkflow`.
- Keep `runs` as the ledger service. `PageRunWorkflow` records through
  `RunsService`; it does not own persistence.
- Keep `app.py` as the composition root. It wires one page-run workflow per
  lifecycle operation because each operation has a different mutation policy
  label.
- Do not port the full `../almanac` finalizer/source-refresh machinery in this
  slice. Python ingest still uses local `SourceRuntime`; pending-source
  finalizers are not the current product shape.

## Shape

```python
context = page_runs.begin(
    PageRunBeginRequest(cwd=request.cwd, wiki=request.wiki, run_id=run_id)
)

# operation-specific preparation stays here
page_runs.record(context, RunEventKind.MESSAGE, "resolved 1 source")
prompt = render_ingest_prompt(...)

result = page_runs.execute(
    PageRunExecuteRequest(
        context=context,
        harness=request.harness,
        prompt=prompt,
        title=request.title,
        success_summary="ingest completed",
    )
)
```

`begin` owns the transition to `running` and the mutation preflight. `execute`
owns the harness call, transcript/event recording, mutation validation, index
refresh, and terminal success. `fail` owns error recording and terminal failure.

## Cosmic Python Transfer

Chapter 4 says it often makes sense to split out a service layer when endpoint
code is doing orchestration such as fetching, validating, error handling, and
committing. Here, the duplicate orchestration is inside workflows rather than a
web endpoint, but the transfer is the same: a named application workflow should
own the boring steps that every page-writing operation repeats.

Chapter 13 describes the composition root as the place where setup moves so
entrypoints do not construct and pass dependencies around. This slice keeps
that direction: `app.py` wires `PageRunWorkflow`; ingest and garden receive it
explicitly.

## Files

- `src/codealmanac/workflows/page_run/`
- `src/codealmanac/workflows/ingest/service.py`
- `src/codealmanac/workflows/garden/service.py`
- `src/codealmanac/app.py`
- `tests/test_architecture.py`
- `tests/test_ingest_workflow.py`
- `tests/test_garden_workflow.py`
- `docs/python-port/next-agent-brief.md`
- `docs/python-port/worklog.md`

## Verification

Run focused behavior checks:

```bash
uv run pytest tests/test_ingest_workflow.py tests/test_garden_workflow.py tests/test_architecture.py
uv run ruff check src/codealmanac/workflows src/codealmanac/app.py tests/test_architecture.py tests/test_ingest_workflow.py tests/test_garden_workflow.py
```

Then run the broad gates:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
