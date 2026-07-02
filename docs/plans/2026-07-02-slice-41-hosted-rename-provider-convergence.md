# Hosted Rename Provider Convergence Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Finish the active `usealmanac` to `codealmanac-hosted` identity rename across runtime code, deployment metadata, and provider verification.

**Architecture:** Treat historical docs as history, but make active code, active agent guidance, runtime defaults, and provider-facing names say `codealmanac-hosted`. Provider checks stay explicit and auditable; Vercel is the only observed provider project name mismatch and should be renamed through the documented REST project update API if the local Vercel token has permission.

**Tech Stack:** Hosted FastAPI backend settings and logging, Next.js frontend config, GitHub CLI, Vercel CLI/API, Render CLI, Modal CLI, Doppler CLI, pytest, Ruff, Next lint/build.

---

## Scope

Implement now:

- Update active hosted repo guidance from `usealmanac` to `codealmanac-hosted`.
- Update active backend runtime names and logger/event-dispatch keys that still say `usealmanac`.
- Update active frontend default contact/product config away from `usealmanac`.
- Update active deployment/provider docs with the observed GitHub, Vercel, Render, Doppler, Modal, PostHog, and Autumn CLI state.
- Rename the Vercel project from `usealmanac` to `codealmanac-hosted` through the documented Vercel REST API if the authenticated local Vercel token can do it.
- Deploy or verify production after the active rename changes.

Defer:

- Rewriting historical worklogs and old design docs where `usealmanac` names the historical repo or event.
- Deleting the old Modal `usealmanac-updates` app unless we have a deliberate provider-cleanup step.
- Renaming the dirty `/Users/rohan/Desktop/Projects/usealmanac` folder; the active work happens in the clean hosted worktree.

## Current Evidence

Observed on 2026-07-02:

- GitHub repo exists as `AlmanacCode/codealmanac-hosted` with default branch `main`.
- Hosted clean worktree origin is `https://github.com/AlmanacCode/codealmanac-hosted.git`.
- Vercel project is still `thealmanac/usealmanac`, id `prj_sBOdSIF82roDGnkFeYrh5qdg6epp`.
- Vercel public docs expose `PATCH /v9/projects/{idOrName}` with a `name` body field.
- Render service `codealmanac-backend` points at `https://github.com/AlmanacCode/codealmanac-hosted`, branch `main`, health `/api/health`.
- Doppler project `codealmanac` has `dev`, `dev_personal`, `stg`, and `prd`.
- Modal has both `usealmanac-updates` and `codealmanac-hosted-updates` deployed.
- `posthog-cli` is installed.
- `atmn` is not globally installed, but the hosted frontend has it as an npm dev dependency and exposes billing scripts.

## Design Wireframe

```text
active code names
  CLAUDE.md / MANUAL.md / app title / logger keys / frontend defaults

provider truth
  gh repo view                 -> codealmanac-hosted
  vercel inspect/patch         -> codealmanac-hosted
  render services list         -> codealmanac-backend
  modal app list               -> codealmanac-hosted-updates
  doppler configs/secrets      -> codealmanac

launch docs
  deployment runbook records what was verified, changed, or intentionally left.
```

## Task 1: Active Runtime Rename

**Files:**

- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/CLAUDE.md`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/MANUAL.md`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/server/app.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/server/errors.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/services/events/dispatcher.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/services/identity/accounts/service.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/lib/config.ts`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/supabase/migrations/20260620000000_init.sql`

**Steps:**

1. Rename active agent-facing docs to `codealmanac-hosted`.
2. Rename FastAPI title to `codealmanac-hosted backend`.
3. Rename loggers and domain-event session keys from `usealmanac...` to stable `codealmanac_hosted...` names.
4. Rename frontend default email/product URL fallbacks away from `usealmanac`.
5. Update the clean-slate Supabase migration comment only; do not rewrite historical migrations beyond active schema naming.

## Task 2: Provider Rename And Verification

**Files:**

- Modify if needed: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/.github/workflows/deploy.yml`
- Modify if needed: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/render.yaml`
- Modify if needed: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/vercel.json`
- Modify if needed: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/vercel.json`

**Steps:**

1. Verify GitHub repo name and default branch with `gh repo view`.
2. Rename Vercel project to `codealmanac-hosted` using `PATCH /v9/projects/{idOrName}?slug=thealmanac` if the local token can be used.
3. Re-inspect Vercel with `vercel project inspect codealmanac-hosted --scope thealmanac`.
4. Verify Render still points at `AlmanacCode/codealmanac-hosted`.
5. Verify Doppler project/config names.
6. Verify Modal contains `codealmanac-hosted-updates`.
7. Verify PostHog CLI availability and Autumn npm-script availability without mutating billing state.

## Task 3: Production Smoke

**Files:**

- No code files expected unless verification exposes a real deployment config issue.

**Steps:**

1. Run hosted backend focused tests for changed runtime files.
2. Run hosted frontend route/component/lint/build gates.
3. Deploy frontend production if build succeeds and provider state is aligned.
4. Trigger Render deploy or verify latest live service if backend code changed.
5. Verify `https://www.codealmanac.com` and `https://codealmanac-backend-docker.onrender.com/api/health`.

## Task 4: Launch Docs And Milestone

**Files:**

- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/deployment-rename-runbook.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/verification-matrix.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/worklog.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/next-agent-brief.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/progress.md`

**Steps:**

1. Record the exact provider commands and outcomes.
2. Update progress estimates.
3. Commit and push hosted changes.
4. Commit and push launch docs.
5. Send RelayForge with what changed, what was verified, and what remains.

## Verification

Hosted backend:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_events_contract.py tests/test_identity_auth_contract.py tests/test_architecture_contract.py -q
uv run ruff check .
uv run python -m compileall src modal_app -q
git diff --check
```

Hosted frontend:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run test:routes
npm run test:frontend
npm run lint
npm run build
```

Provider checks:

```bash
gh repo view AlmanacCode/codealmanac-hosted --json nameWithOwner,url,defaultBranchRef
vercel project inspect codealmanac-hosted --scope thealmanac
render services list --output json
doppler configs --project codealmanac --json
modal app list --json
posthog-cli --help
npm run billing:verify
```
