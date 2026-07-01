# Slice 95 - Sync Policy Extraction

## Scope

Split deterministic sync cursor and ledger rules out of
`workflows/sync/service.py` without changing public `sync` behavior.

## Read Before Coding

- `MANUAL.md`
- `docs/python-port-live-agreement.md`
- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_05_high_gear_low_gear.md`
- `.almanac/pages/capture-ledger.md`
- `.almanac/pages/capture-flow.md`

Cosmic Python frames the service layer as the place that defines workflows and
use cases. The relevant line here is that service-layer code defines "what we
need to get from our repositories, what pre-checks and current state validation
we should do, and what we save at the end." The sync workflow should coordinate
those steps, while cursor decisions should be independently readable policy.

## Shape

```python
app.workflows.sync.run(request)
  -> discover transcript candidates
  -> scope to selected wiki
  -> load run records and sync ledgers
  -> sync.policy.evaluate_cursor(...)
  -> sync.policy.reconcile_pending_entry(...)
  -> start foreground ingest or enqueue background ingest
  -> persist policy-produced ledger entries
```

`workflows/sync/service.py` remains the orchestration entrypoint. It may call
sources, workspaces, runs, ingest, queue, and the ledger store.

`workflows/sync/policy.py` owns pure deterministic rules:

- ledger key and fallback identity matching
- transcript snapshot reading and cursor hashing
- quiet-window and internal-transcript skips
- pending, absorbed, failed, and needs-attention entry transitions
- pending-run reconciliation
- generated ingest title and cursor guidance text

## Out Of Scope

- No command spelling changes.
- No ledger schema changes.
- No sync behavior changes.
- No new background worker behavior.
- No prompt changes beyond moving existing cursor guidance.

## Tests

- Focused sync workflow tests.
- Architecture test that `SyncWorkflow` does not regrow ledger/cursor helpers.
- Architecture test that `sync.policy` does not import orchestration services or
  integrations.
- Full pytest, ruff, and diff hygiene.
