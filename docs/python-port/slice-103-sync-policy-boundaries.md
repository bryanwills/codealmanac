# Slice 103: Sync Policy Boundaries

## Scope

Split `workflows/sync/policy.py` into a facade over focused deterministic
policy modules:

- `snapshots.py` owns transcript snapshot reading, line counting, and content
  hashes.
- `entries.py` owns ledger-entry state transitions.
- `identity.py` owns workspace/session/ledger identity helpers.
- `decisions.py` owns cursor decisions and pending-run reconciliation.
- `reporting.py` owns skip/start summary row construction.
- `guidance.py` owns generated Ingest title and cursor guidance.
- `policy.py` remains the import facade used by `SyncWorkflow`.

## Out Of Scope

- No sync behavior changes.
- No ledger schema changes.
- No background-job policy changes.
- No new automation behavior.

## Design Notes

Slice 95 correctly separated sync orchestration from deterministic sync policy.
The current pressure is inside that policy module: it now mixes transcript IO,
cursor hashing, ledger identity, pending reconciliation, transition builders,
summary row construction, and prompt guidance in one 417-line file.

Cosmic Python's service-layer chapter distinguishes orchestration from lower
level behavior: it says an application service "drives the application by
following a bunch of simple steps" and warns that putting too much logic into
the service layer can produce an anemic domain
(`docs/reference/cosmic-python/chapter_04_service_layer.md`). For CodeAlmanac,
`SyncWorkflow` should continue to drive the use case; the deterministic sync
rules should have names that match their reasons to change.

## Files

- `src/codealmanac/workflows/sync/policy.py`
- `src/codealmanac/workflows/sync/snapshots.py`
- `src/codealmanac/workflows/sync/entries.py`
- `src/codealmanac/workflows/sync/identity.py`
- `src/codealmanac/workflows/sync/decisions.py`
- `src/codealmanac/workflows/sync/reporting.py`
- `src/codealmanac/workflows/sync/guidance.py`
- `tests/test_architecture.py`
- `docs/python-port-live-agreement.md`
- `docs/python-port/ownership-map.md`
- `docs/python-port/idea-evolution.md`
- `docs/python-port/next-agent-brief.md`
- `docs/python-port/verification-matrix.md`
- `docs/python-port/worklog.md`

## Tests

- Architecture guard: sync service remains orchestration-only and sync policy
  stays split by rule family.
- Focused sync workflow tests for status, foreground run, background run, and
  pending reconciliation.
- Public CLI dogfood for `sync status` against a temp transcript if practical;
  otherwise focused service tests remain the behavior proof.
- Full `uv run pytest`.
- Full `uv run ruff check .`.

