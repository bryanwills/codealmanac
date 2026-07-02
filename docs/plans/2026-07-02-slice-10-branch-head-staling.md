# Slice 10 Plan: Branch Head Staling

Date: 2026-07-02.
Status: planned.

## Goal

When a branch advances to a newer head, older queued or running runs for that
branch should become `stale`. This handles the expected-head mismatch case
before delivery.

## Behavior

During trigger recording for a configured branch:

```text
new head arrives
  -> older pending trigger events become superseded
  -> queued/running runs on the same branch with a different expected_head_sha
     become stale
  -> each stale run gets a normalized run event
  -> new pending trigger event is inserted
```

Terminal runs are not touched.

Runs whose `expected_head_sha` already equals the new head are not touched.

## Ownership

- `ControlStore.record_trigger_event_in_connection(...)` owns this transition
  because it already runs inside the control DB transaction that observes the
  branch's new head.
- The service facade stays thin.
- No Git, CLI, worker, or delivery behavior is added here.

## Required Seam

Add:

```python
app.control.get_run(GetControlRunRequest(...))
```

This lets tests and later workflows read the updated run row without reaching
into the store.

## Tests

- Newer trigger marks older queued run stale.
- Newer trigger marks older running run stale.
- Staling appends ordered run events.
- Terminal runs are not modified.
- Runs for the same expected head are not modified.
- Duplicate-head trigger behavior remains unchanged.

## Docs

- Update worklog, verification matrix, progress, and next-agent brief.
- Send RelayForge update after full verification and push.
