# Slice 67: Branch-triggered source bundles

## Intent

Cloud should update from a maintained-branch finalization event. Captured
conversations are a source library; a branch trigger selects the relevant source
bundle and starts one run. The old timer-shaped conversation ingest path must
not be the only path that can turn captured sessions into a run.

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `docs/codealmanac-launch/schema-contract.md`
- `docs/codealmanac-launch/cli-contract.md`
- `docs/reference/cosmic-python/chapter_02_repository.md`
- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_05_high_gear_low_gear.md`
- `docs/reference/cosmic-python/chapter_06_uow.md`

## Current Evidence

- `BranchPushUpdates.plan(...)` already enforces enabled trigger policies and
  uses the policy delivery mode.
- `ConversationIngestUpdates.start_due_conversation_ingests(...)` still creates
  conversation-batch runs from a 5-hour due state and hard-codes commit delivery.
- `RunQueue.conversation_batch(...)` already supports policy-driven `commit` or
  `pr` delivery for `ConversationBatchSource`.
- `ConversationsStore` already stores `source_ref` by session and can create a
  `ConversationBatchSource` from claimed turns.

## Target Shape

```python
outcome = updates.branches.plan(event)

policy = repositories.trigger_policy(repo_id, branch)
pending = conversations.claim_triggered_batch(repo_id, branch)

if pending.has_refs:
    queue.conversation_batch(..., delivery_mode=policy.delivery_mode)
else:
    queue.branch_push(..., delivery_mode=policy.delivery_mode)
```

The service owns the product decision. The store owns the claim query. The
worker still receives refs, not rendered source text.

## Scope

- Add a store method that claims pending completed conversation turns for a
  specific repo and branch at trigger time.
- Make branch-push planning prefer a `ConversationBatchSource` run when the
  branch has captured source refs.
- Preserve `BranchSource` fallback for branches without captured source refs.
- Respect the maintained branch delivery mode for both source shapes.
- Keep retry, completion, stale handling, and artifact-by-reference behavior.

## Out Of Scope

- Broad GitHub webhook family expansion.
- Login-time or background reconciliation.
- Removing the timer method entirely in this slice.
- Frontend or CLI command changes.

## Verification

- Hosted focused tests for branch push with pending conversation refs.
- Hosted focused tests for policy-driven PR delivery on conversation batches.
- Hosted focused tests proving branch fallback still works.
- Hosted conversation scheduler tests adjusted only where the old commit-only
  assumption conflicts with shared queue behavior.
- `uv run ruff check .`
- `git diff --check`

## Result

- Implemented in hosted backend.
- Verified with:
  - `uv run pytest tests/test_updates_contract.py tests/test_conversation_ingest_scheduler.py -q`
    (`61 passed`)
  - `uv run pytest tests/test_updates_contract.py tests/test_conversation_ingest_scheduler.py tests/test_modal_worker_contract.py tests/test_github_service_contract.py tests/test_installations_contract.py tests/test_architecture_contract.py -q`
    (`172 passed`)
  - `uv run pytest -q` (`380 passed`, `1` Starlette warning)
  - `uv run ruff check .`
  - `python -m compileall backend/src -q`
  - `git diff --check`
