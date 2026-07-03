# Slice 76 Hosted Repository Settings UX Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make hosted repository setup/settings feel like the cloud product contract: GitHub App access, capture, maintained branches, and per-branch delivery are clear, actionable, and aligned with backend DTOs.

**Architecture:** This is a frontend-facing slice. Backend behavior already exposes the right repository-list DTO shape; the frontend must mirror it exactly. Repository settings stay split into a readiness summary and an editor: summary explains readiness, form mutates branch and same-PR policies through the BFF.

**Tech Stack:** Next.js 16, React 19, server/BFF DTOs, node:test frontend static-render tests.

---

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `docs/codealmanac-launch/cli-contract.md`
- `docs/codealmanac-launch/frontend-surface-contract.md`
- `frontend/src/components/repositories/setup-summary.tsx`
- `frontend/src/components/repositories/settings-form.tsx`
- `frontend/src/lib/api/dto/repositories.ts`

## Design Wireframe

```tsx
RepositorySettingsPage
  data = Promise.all(repo, branches, triggerPolicies, captureStatus)
  <RepositorySetupSummary data={data} />
  <RepositorySettingsForm data={data} />

RepositorySetupSummary
  rows:
    GitHub App       -> connected account + Configure GitHub
    Repository       -> repo full name + write/read permission
    Capture          -> credential state + CLI setup action
    Maintained       -> enabled branch names
    Delivery         -> delivery modes derived from enabled branch policies

RepositorySettingsForm
  Same-repo PRs      -> repo.settings.sameRepo
  Branch policies    -> one row per branch
    checkbox         -> trigger enabled
    delivery buttons -> commit/pr, disabled until branch enabled
```

## Tasks

### Task 1: Align Repository List DTOs

**Files:**
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/codex-slice-74-github-rate-limit/frontend/src/lib/api/dto/repositories.ts`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/codex-slice-74-github-rate-limit/frontend/src/components/repositories/repository-list.tsx`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/codex-slice-74-github-rate-limit/frontend/src/app/design-lab/_experiments/atlas/mock.ts`

**Steps:**
1. Add `accountId` and `defaultBranch` to `RepositoryListItemDTO`.
2. Update comments/mocks that still say the list is only `repoId + fullName`.
3. Keep repository list rendering austere; do not invent status fields.

### Task 2: Polish Readiness Summary

**Files:**
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/codex-slice-74-github-rate-limit/frontend/src/components/repositories/setup-summary.tsx`
- Modify tests: `/Users/rohan/.config/superpowers/worktrees/usealmanac/codex-slice-74-github-rate-limit/frontend/tests/frontend/repository-setup-summary.test.tsx`

**Steps:**
1. Keep summary factual and compact.
2. Replace “Not installed” capture status with language that matches cloud capture: “Setup needed” / “Credential issued”.
3. Add a direct CLI guide action near capture without claiming the browser can install local hooks.
4. Preserve GitHub configuration action.

### Task 3: Make Branch Policy Rows Read Correctly

**Files:**
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/codex-slice-74-github-rate-limit/frontend/src/components/repositories/settings-form.tsx`
- Modify tests: `/Users/rohan/.config/superpowers/worktrees/usealmanac/codex-slice-74-github-rate-limit/frontend/tests/frontend/repository-settings.test.tsx`

**Steps:**
1. Make each branch row show branch name, default/SHA detail, maintained/ignored state, and delivery controls.
2. Delivery remains per branch and disabled until that branch is enabled.
3. Avoid nested cards and marketing copy; keep dashboard density.

### Task 4: Verify And Document

**Commands:**
- `npm run test:frontend`
- `npm run test:routes`
- `npm run lint`
- `npm run build`
- `git diff --check`

**Docs:**
- Update `docs/codealmanac-launch/worklog.md`
- Update `docs/codealmanac-launch/verification-matrix.md`
- Update `docs/codealmanac-launch/next-agent-brief.md`

**Deploy:**
- Push hosted changes to hosted `main` and verify Vercel production.
- Use Chrome to verify the production repository settings page renders the revised summary and branch rows.
