# Slice 2: Local Trigger Policy And Event Recording

Date: 2026-07-02.
Status: implemented.

## Goal

Make the local control DB writable for repository policy and local trigger
events.

This slice does not install Git hooks or start workers. It creates the product
verb that future hook dispatchers, explicit local commands, and cloud-parallel
code can call:

```python
repo = app.control.upsert_repository(...)
branch = app.control.set_branch_policy(...)
event = app.control.record_trigger_event(...)
```

## Read Before Coding

- `MANUAL.md`
- `docs/codealmanac-launch/schema-contract.md`
- `docs/codealmanac-launch/ownership-map.md`
- `docs/codealmanac-launch/verification-matrix.md`
- `docs/hosted-local-live-agreement/local-pipeline-architecture-2026-07-02.md`
- `src/codealmanac/services/control/`
- `src/codealmanac/integrations/workspaces/git/probe.py`
- `tests/test_control_service.py`

## Current Evidence

- Slice 1 created the control schema and `app.control.ensure_ready()`.
- Local trigger policy is recorded in the `branches` table.
- `trigger_events.status` supports `pending`, `claimed`, `ignored`, and
  `superseded`.
- Git hooks are repo-level; branch filtering must be a CodeAlmanac control DB
  decision.

## Target Shape

```python
repo = app.control.upsert_repository(
    UpsertRepositoryRequest(
        provider="github",
        owner_login="AlmanacCode",
        name="codealmanac",
        full_name="AlmanacCode/codealmanac",
        almanac_root=Path("almanac"),
        local_root_path=repo_path,
    )
)

app.control.set_branch_policy(
    SetBranchPolicyRequest(
        repository_id=repo.id,
        name="dev",
        trigger_enabled=True,
        delivery_mode=ControlDeliveryMode.COMMIT,
    )
)

result = app.control.record_trigger_event(
    RecordTriggerEventRequest(
        repository_id=repo.id,
        branch_name="dev",
        kind=TriggerEventKind.LOCAL_POST_COMMIT,
        head_sha="abc123",
        previous_head_sha="def456",
    )
)
```

Disabled or unknown branches return `recorded=False` and write no
`trigger_events` row. A new pending trigger for a branch marks older pending
triggers for that branch as `superseded`.

## Out Of Scope

- Installing or repairing Git hooks.
- Parsing Git remotes into owner/repo automatically.
- Claiming trigger events for worker runs.
- Creating `runs` rows from trigger events.
- Cancelling active runs when a newer head arrives.
- Delivery to working tree, commit, or PR.

## Implementation Plan

1. Add control enums and row models for repositories, branches, and trigger
   events.
2. Add request models for repository upsert, branch policy, trigger event
   recording, and trigger event listing.
3. Add deterministic local ids for repository and branch rows.
4. Add store methods that:
   - upsert repositories;
   - set branch trigger/delivery policy;
   - ignore disabled branches without writing event rows;
   - insert pending trigger events for enabled branches;
   - supersede older pending trigger events for the same branch.
5. Keep `ControlService` as the thin product facade over the store.
6. Add focused tests for policy upsert, disabled branch filtering, pending
   event creation, and superseding older pending events.
7. Update launch worklog, verification matrix, and next-agent brief.

## Verification

Run:

```bash
uv run pytest tests/test_control_service.py tests/test_architecture.py
git diff --check
```

Run full `uv run pytest` before committing because this extends the app-level
control service contract.

## Result

Implemented writable local control service verbs for repository policy and
trigger event recording:

```python
app.control.upsert_repository(...)
app.control.set_branch_policy(...)
app.control.record_trigger_event(...)
app.control.list_trigger_events(...)
```

Disabled or unknown branches write no `trigger_events` row. Enabled branches
write a pending event. A newer pending head marks older pending events for that
branch as `superseded`.

Focused verification passed:

```text
uv run pytest tests/test_control_service.py tests/test_architecture.py
59 passed

git diff --check
passed
```
