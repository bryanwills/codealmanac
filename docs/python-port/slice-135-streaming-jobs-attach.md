# Slice 135: Streaming Jobs Attach

## Goal

Make `codealmanac jobs attach <run-id>` match the live agreement and archived
behavior: it should stream a job's event log until the run reaches a terminal
status, not print a one-time snapshot.

## Why This Slice

The active goal explicitly includes background jobs with `attach/cancel`.
Python already has `jobs attach`, but current dispatch calls
`RunsService.attach(...)` and renders a snapshot. The live agreement says
`jobs attach` streams a running job's event log, and the archived TypeScript CLI
described the command as "stream a job log until the job exits."

This is not cosmetic. A background job surface without streaming attach makes
running jobs harder to inspect and diverges from the product contract.

## Architecture

Keep `RunStore` as the repository facade. Cosmic Python's repository chapter
describes a repository as "a simplifying abstraction over data storage"; polling
until terminal is a use case, not data storage.

Add a small service-side streamer:

```python
updates = app.runs.stream_attach(
    StreamRunAttachRequest(cwd=Path.cwd(), run_id=run_id)
)
render_run_attach_stream(updates, json_output=args.json)
```

Expected responsibility split:

- `services/runs/store.py`: read records and events, no polling loop.
- `services/runs/streaming.py`: poll `RunStore.attach(...)`, emit only new
  events, stop at `done`, `failed`, or `cancelled`.
- `services/runs/service.py`: resolve workspace and expose the use case.
- `cli/dispatch/jobs.py`: call the streaming use case for `jobs attach`.
- `cli/render/jobs.py`: render attach updates incrementally.

## Scope

In scope:

- Add typed `StreamRunAttachRequest` and `RunAttachUpdate`.
- Stream only new events after the initial replay.
- Stop when the run record becomes terminal.
- Wait one bounded poll when a terminal record is visible but its terminal
  status event is not yet in the JSONL log; `RunTransitionWriter` writes the
  record just before appending the event.
- Flush text output as events arrive.
- Preserve `jobs logs` as the snapshot command.
- Update command help to say queued or running cancellation.
- Add tests for the streaming service and CLI terminal attach behavior.

Out of scope:

- Browser-side cancel/attach controls.
- Killing provider processes from cancel.
- Stale-process display status.
- Public `--poll-interval` flag.

## Verification

Run focused tests:

```bash
uv run pytest tests/test_runs_service.py tests/test_cli.py::test_cli_jobs_inspects_local_run_records
```

Run architecture/public contract tests if boundary files change:

```bash
uv run pytest tests/test_architecture.py tests/test_public_contract.py
```

Dogfood:

```bash
uv run codealmanac jobs attach <terminal-run-id>
```

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
