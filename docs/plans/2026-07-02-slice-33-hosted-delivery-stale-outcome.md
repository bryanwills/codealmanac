# Hosted Delivery Stale Outcome Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make hosted update completion record deterministic branch-head drift as a terminal `stale` run outcome instead of leaking a delivery exception through the internal completion route.

**Architecture:** Delivery remains the only GitHub writer. The GitHub integration exposes a typed branch-head drift error, `services/updates/delivery.py` maps it to a product `StaleDelivery`, and `UpdateCompletion` records `RunStatus.STALE` with a run event and no billing/domain delivery event. Frontend/API DTOs learn the same `stale` status so the dashboard can render the real backend state.

**Tech Stack:** Python FastAPI backend, SQLModel/Supabase Postgres schema, Pydantic DTOs, Next.js/TypeScript frontend status components, pytest, node:test.

---

## Read Before Coding

- `/Users/rohan/.codex/skills/slow-development/SKILL.md`
- `/Users/rohan/.codex/skills/python-code-quality/SKILL.md`
- `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/AGENTS.md`
- `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/MANUAL.md`
- Hosted wiki pages: `backend-update-pipeline`, `update-bundle-contract`, `update-pipeline-vocabulary`, `update-source-boundary`

## Design Decision

Use `stale`, not `failed`, when delivery cannot write because the target branch no longer has the expected head SHA. This is not an agent error and not a successful delivery. It means the run was based on an old branch snapshot and a newer trigger/run should own the current branch state.

Do not add automatic retry machinery in this slice. GitHub already sends a new trigger for the newer head, and conversation ingestion already re-selects branch head at run creation. The slice only guarantees the old run terminates cleanly.

Do not add stale GitHub check fanout in this slice. Existing failed worker bundles also do not dispatch a failure domain event today; check fanout needs a separate, broader terminal-run fanout slice.

## Wireframe

```python
try:
    commit_sha = delivery.apply(run=run, bundle=bundle)
except StaleDelivery as stale:
    stale_run = store.mark_stale(
        run_id,
        summary=bundle.summary,
        reason=stale.reason,
        expected_head_sha=stale.expected_head_sha,
        actual_head_sha=stale.actual_head_sha,
    )
    conversations_store.mark_ingest_run_stale(... only for ConversationBatchSource ...)
    return UpdateResult.stale(stale_run, stale.reason)

delivered = store.mark_delivered(...)
events.dispatch([RunDelivered(...)])
return UpdateResult.delivered(delivered)
```

## Task 1: Backend Status Contract

**Files:**
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/services/updates/models.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/server/dtos/runs.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/supabase/migrations/20260620000000_init.sql`

**Steps:**
1. Add `RunStatus.STALE = "stale"`.
2. Include stale in `Run.is_terminal`.
3. Add `UpdateResult.kind == "stale"` and `UpdateResult.stale(run, reason)`.
4. Extend `RunDTO.status` literal with `"stale"`.
5. Extend the migration status check to include `"stale"`.

## Task 2: Typed Delivery Conflict

**Files:**
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/integrations/github/errors.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/integrations/github/__init__.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/integrations/github/resources/git.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/services/updates/delivery.py`
- Test: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/tests/test_github_git_contract.py`
- Test: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/tests/test_updates_contract.py`

**Steps:**
1. Add a typed `GitHubBranchHeadChanged` exception carrying repo, branch, expected SHA, and actual SHA.
2. Raise `GitHubBranchHeadChanged` from `GitHubGitIntegration.commit_files` instead of raw `ValueError` when the branch ref no longer matches the expected head.
3. Add product-level `StaleDelivery` in `services/updates/delivery.py`.
4. Preflight `CommitToBranch` with `github.git.branch_head(repo, branch)` before commit; stale if current head differs.
5. Preflight `OpenWikiPullRequest` with `github.git.branch_head(repo, base_branch)` before branch creation; stale if current base differs.
6. Wrap `GitHubBranchHeadChanged` from the commit race window into `StaleDelivery`.
7. Keep `expected_head_sha` on the final commit call as defense in depth.

## Task 3: Completion Persistence

**Files:**
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/services/updates/store.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/services/updates/completion.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/services/conversations/models.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/services/conversations/store.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/server/dtos/conversation_sources.py`
- Test: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/tests/test_updates_contract.py`
- Test: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/tests/test_update_run_events_contract.py`

**Steps:**
1. Add `UpdatesStore.mark_stale(...)` that writes `runs.status = "stale"`, stores summary/error reason, sets `finished_at`, and appends a `run_events` status event with expected/actual SHA payload.
2. Catch `StaleDelivery` in `UpdateCompletion.complete`.
3. Return `UpdateResult.stale`.
4. Do not dispatch `RunDelivered` and do not record billing for stale runs.
5. Add `mark_ingest_run_stale` for conversation-batch runs so active state clears and branch summaries can render `stale`.
6. Extend conversation status DTO/types to include `"stale"`.

## Task 4: Frontend Status Surface

**Files:**
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/lib/api/dto/common.ts`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/lib/api/dto/conversation-sources.ts`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/components/runs/run-status.ts`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/components/ui/status-icon.tsx`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/app/design-lab/_experiments/RunStatusLab.tsx`
- Test: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/tests/frontend/format.test.ts`

**Steps:**
1. Add `"stale"` to `RunStatus`.
2. Add `"stale"` to conversation branch latest-run status.
3. Add user-facing label `"Stale"` and a muted status color.
4. Reuse a simple status glyph shape rather than inventing a decorative new component.
5. Update format/design-lab tests or fixtures that enumerate statuses.

## Task 5: Verification and Docs

**Commands:**
- Hosted backend targeted:
  - `cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend && uv run pytest tests/test_updates_contract.py tests/test_update_run_events_contract.py tests/test_github_git_contract.py tests/test_repositories_api_contract.py -q`
- Hosted frontend targeted:
  - `cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend && npm run test:frontend -- --runInBand`
  - If the command shape differs, inspect `package.json` and run the existing frontend test command.
- Hosted hygiene:
  - `cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend && uv run ruff check . && uv run ruff format --check . && python -m compileall src modal_app -q && git diff --check`
- Full hosted backend before commit:
  - `cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend && uv run pytest -q`

**Docs:**
- Update local launch docs:
  - `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/worklog.md`
  - `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/progress.md`
  - `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/verification-matrix.md`
  - `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/next-agent-brief.md`

**Commit Plan:**
1. Commit hosted implementation: `feat: record stale delivery outcomes`
2. Commit local launch docs: `docs: record hosted stale delivery slice`
3. Push both branches.
4. Send RelayForge update.
