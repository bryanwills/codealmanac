# Slice 5: Control Run Ledger

Date: 2026-07-02.
Status: implemented.

## Goal

Add SQL-backed run records and ordered run events to the local control service.

This slice does not replace the existing repo-local `almanac/jobs/*.json` run
files. It creates the control DB seam that local workers and hosted workers can
share conceptually.

## Target Shape

```python
run = app.control.create_run(CreateControlRunRequest(...))
app.control.update_run(UpdateControlRunRequest(...))
event = app.control.append_run_event(AppendControlRunEventRequest(...))
events = app.control.list_run_events(ListControlRunEventsRequest(run_id=run.id))
```

## Behavior

- Runs belong to a repository and branch.
- Runs may point to a trigger event.
- Run status uses launch vocabulary:
  `queued`, `running`, `succeeded`, `failed`, `stale`, `cancelled`.
- Run events are ordered per run with sequence numbers starting at `1`.
- Run events use launch event kinds:
  `status`, `message`, `tool`, `output`, `error`.
- Bulky data stays by reference through `source_bundle_ref`, `request_ref`,
  `result_ref`, `event_json`, and `artifact_ref`.

## Out Of Scope

- Migrating existing repo-local job files.
- Queue claiming or locking.
- Worker execution.
- Delivery rows.
- Supabase/cloud migrations.

## Implementation Plan

1. Add control run status/event enums and record models.
2. Add request models for create/update/list run operations.
3. Add store methods for creating runs, updating runs, appending events, and
   listing events.
4. Expose the methods through `ControlService`.
5. Add tests proving run rows, event sequencing, and status updates.
6. Update launch docs/worklog/verification evidence.

## Verification

Run:

```bash
uv run pytest tests/test_control_service.py tests/test_architecture.py
uv run ruff check .
git diff --check
```

Run full `uv run pytest` before committing.

## Result

Implemented SQL-backed run records and ordered run events through
`app.control`:

```python
app.control.create_run(...)
app.control.update_run(...)
app.control.append_run_event(...)
app.control.list_run_events(...)
```

Runs use launch statuses: `queued`, `running`, `succeeded`, `failed`, `stale`,
and `cancelled`. Run events are sequenced per run starting at `1`.

Focused verification passed:

```text
uv run pytest tests/test_control_service.py tests/test_architecture.py
64 passed

uv run ruff check .
passed

git diff --check
passed
```
