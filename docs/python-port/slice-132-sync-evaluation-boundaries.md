# Slice 132: Sync Evaluation Boundaries

## Scope

Keep `codealmanac sync` and `codealmanac sync status` behavior unchanged while
splitting sync candidate evaluation out of the `SyncWorkflow` facade.

## Out of scope

- No sync cursor policy changes.
- No ledger schema changes.
- No foreground/background execution changes.
- No transcript discovery adapter changes.

## Design

Cosmic Python chapter 4 describes the service layer as "a single place to
capture all the use cases" (`docs/reference/cosmic-python/chapter_04_service_layer.md`),
while chapter 13 argues for explicit dependencies over "an implicit dependency
on a specific detail" (`docs/reference/cosmic-python/chapter_13_dependency_injection.md`).
For this slice, `SyncWorkflow` remains the explicit use-case facade, and the
candidate evaluator becomes a named collaborator composed by the facade.

Slices 103 and 109 already split deterministic sync policy and execution
effects; the remaining pressure is the `SyncWorkflow.evaluate(...)` loop, which
still performs discovery, scoping, ledger reads, pending-run reconciliation,
cursor decisions, and summary assembly in one service file.

The split is:

```python
workflows.sync.service       # SyncWorkflow facade: status/run orchestration
  -> evaluation.py           # SyncEvaluator: discovery/scoping/evaluation
  -> execution.py            # SyncRunExecutor: foreground/background effects
  -> policy.py               # deterministic sync rules facade
```

`SyncWorkflow` keeps the public `status`, `run`, and `evaluate` methods. The
`evaluate` method delegates to `SyncEvaluator` so tests and future callers can
still use the workflow as the entrypoint.

## Verification

- Existing sync workflow tests.
- Existing sync CLI tests through the full test suite.
- Architecture guard that keeps candidate evaluation mechanics out of
  `service.py` and execution effects out of `evaluation.py`.
- Public CLI dogfood for `codealmanac sync status --json` in this checkout.
- Full pytest, Ruff, and diff checks.
