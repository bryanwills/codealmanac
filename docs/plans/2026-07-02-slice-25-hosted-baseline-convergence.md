# Slice 25 Hosted Baseline Convergence Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Put the current `codealmanac-hosted` deployable branch back on a
single baseline by applying the hosted rename/deploy-surface changes on top of
the latest `origin/main`.

**Architecture:** Do not edit the dirty `../usealmanac` checkout. Use a clean
hosted worktree from `origin/main`, then reapply only the small rename/deploy
surface changes from `origin/codex/cli-hosted-redesign-docs`. Keep the newer
hosted conversation-sync work from `origin/main` intact.

**Tech Stack:** Git worktrees, Python/FastAPI backend, Next.js frontend, Modal,
Vercel package metadata, pytest, ruff, Next build/tests.

**Status:** Implemented and verified on 2026-07-02.

**Result:** Hosted branch `codex/hosted-baseline-convergence` was created from
current `origin/main`, the small rename/deploy-surface change was reapplied,
and commit `1d237db chore: rename hosted deploy surfaces` was pushed to
`origin/codex/hosted-baseline-convergence`.

---

## Scope

- Create an isolated hosted worktree from `origin/main`:

  ```text
  /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence
  ```

- Use branch:

  ```text
  codex/hosted-baseline-convergence
  ```

- Reapply the hosted rename/deploy-surface commit from
  `origin/codex/cli-hosted-redesign-docs` without replacing the newer
  conversation-sync work on `origin/main`.
- Keep product look and routes unchanged.
- Verify backend package metadata, Modal app defaults, frontend package name,
  deploy workflow references, and worker contract tests use CodeAlmanac-hosted
  names.

## Out Of Scope

- WorkOS/AuthKit migration.
- Public `/v1` API design.
- Supabase Auth removal.
- GitHub App permission changes.
- Frontend onboarding redesign.
- Production deploy promotion.

## Design

```text
origin/main
  + hosted conversation sync
  + codealmanac domain docs marker

apply rename surface:
  frontend/package.json              name = codealmanac-hosted
  frontend/package-lock.json         root package name = codealmanac-hosted
  backend/pyproject.toml             name = codealmanac-hosted-backend
  backend/uv.lock                    package name = codealmanac-hosted-backend
  backend/src/almanac/settings.py    modal_app_name = codealmanac-hosted-updates
  backend/modal_app/runtime.py       Modal lookup defaults
  backend/tests/test_modal_worker_contract.py
  .github/workflows/deploy.yml
```

The old `origin/codex/cli-hosted-redesign-docs` branch diverged before hosted
conversation sync. This slice should cherry-pick or manually reapply only the
small rename commit, not merge the whole branch.

## Files

Hosted worktree files to modify:

- `.github/workflows/deploy.yml`
- `backend/modal_app/runtime.py`
- `backend/pyproject.toml`
- `backend/src/almanac/settings.py`
- `backend/tests/test_modal_worker_contract.py`
- `backend/uv.lock`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/app/design-lab/_experiments/atlas/mock.ts`, only if the
  current main still needs the mock DTO repair

CodeAlmanac steering files to update after hosted verification:

- `docs/codealmanac-launch/progress.md`
- `docs/codealmanac-launch/worklog.md`
- `docs/codealmanac-launch/next-agent-brief.md`
- `docs/codealmanac-launch/verification-matrix.md`

## Tests

Hosted focused checks:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_modal_worker_contract.py
uv run ruff check .
uv run ruff format --check .
```

Hosted frontend checks:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm test -- --runInBand
npm run build
```

If `npm test -- --runInBand` is not a valid script contract, run:

```bash
npm run test:routes
npm run test:frontend
```

Final checks:

```bash
git diff --check
git status --short
```

Verified commands:

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest
# 290 passed
uv run ruff check .
# All checks passed
uv run ruff format --check .
# 254 files already formatted
uv run pytest tests/test_modal_worker_contract.py
# 9 passed

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run test:routes
# 26 passed
npm run test:frontend
# 41 passed
npm run build
# succeeded

git status --short --branch
# clean on codex/hosted-baseline-convergence
```

## Implementation Tasks

1. Create the hosted worktree from `origin/main` on
   `codex/hosted-baseline-convergence`.
2. Inspect `origin/codex/cli-hosted-redesign-docs` commit `bc47816` and reapply
   only the rename/deploy-surface changes that still differ on `origin/main`.
3. Confirm the newer conversation-sync files from `origin/main` still exist.
4. Run hosted backend focused tests and lint/format checks.
5. Run hosted frontend route/frontend tests and `npm run build`.
6. Commit and push the hosted slice branch.
7. Send RelayForge with hosted baseline convergence percentages.
8. Update CodeAlmanac launch steering docs and commit/push them on
   `/Users/rohan/Desktop/Projects/codealmanac` `dev`.
