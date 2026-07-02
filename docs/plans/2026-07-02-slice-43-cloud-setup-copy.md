# Cloud Setup Copy Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make hosted setup/onboarding copy match the cloud-first CLI contract: one setup command signs in and asks before installing Claude/Codex capture.

**Architecture:** Keep the existing dashboard routes and account-scoped setup model. Do not reintroduce a separate onboarding state machine. Change only the frontend copy and route tests that define the public setup contract.

**Tech Stack:** Next.js App Router, React Server Components, existing UI components, route-source tests, frontend unit tests, Vercel production deploy.

---

## Scope

Implement now:

- Replace outdated setup instructions that say `almanac login`.
- Present `npx codealmanac@latest setup` as the cloud setup command.
- Explain that setup opens browser login, connects cloud, and asks before installing Claude/Codex capture.
- Rename visible "local agent access" copy to "CodeAlmanac CLI" or "cloud capture" wording where the page is actually about cloud setup.
- Update route tests so future changes cannot reintroduce the old two-command flow.
- Record the live GitHub App permission check from Slice 42: production app has `checks: write`.

Defer:

- Renaming the `/dashboard/local-agent-access` route. The URL is internal and currently wired through existing redirects.
- A new multi-step onboarding wizard. The current design intentionally routes users through GitHub App install, account-scoped repo lists, repository settings, and CLI setup.
- Capture status UI inside the browser. Capture status remains CLI/API-owned for now.

## Current Evidence

- `/dashboard` already owns the GitHub App install prompt.
- `/setup/repo` already resolves CLI-opened repo URLs into account-scoped dashboard pages.
- Repository settings already own maintained branches and per-branch delivery.
- `/dashboard/local-agent-access` currently shows the wrong quickstart:
  `npx codealmanac@latest setup` followed by `almanac login`.
- `/cli-login` currently tells users to rerun `almanac login`; the public command should be `codealmanac login`, with `codealmanac setup` as the primary setup path.
- Production GitHub App permission read returned `checks: write`, so the Slice 42 Check Runs fanout has the required app permission.

## Task 1: Cloud Setup Page Copy

**Files:**

- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/app/dashboard/local-agent-access/page.tsx`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/components/shell/local-agent-access-banner.tsx`

**Steps:**

1. Change the quickstart command to a single line:

   ```text
   npx codealmanac@latest setup
   ```

2. Change the page title from "Set up local agent access" to "Set up the CodeAlmanac CLI".
3. Replace copy about "local .almanac" with cloud setup behavior:
   setup signs in through the browser, connects this machine to cloud, and asks before installing Claude/Codex capture.
4. Change the banner title/copy to match the same contract.
5. Keep the route path and `markLocalAgentSetupIntroSeen` behavior unchanged.

## Task 2: CLI Login Page Copy

**Files:**

- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/app/cli-login/page.tsx`

**Steps:**

1. Replace "Run almanac login again" with "Run codealmanac login again".
2. Replace "Almanac will finish saving the CLI token" with "CodeAlmanac will finish saving the CLI token".
3. Change the CLI page eyebrow to `CodeAlmanac CLI`.
4. Keep the device-login mechanics unchanged.

## Task 3: GitHub App Install Prompt Copy

**Files:**

- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/app/dashboard/page.tsx`
- Modify if needed: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/app/dashboard/accounts/[accountId]/repositories/page.tsx`

**Steps:**

1. Update the empty/install prompt to say `CodeAlmanac GitHub App`.
2. Keep the action URL and account-selection behavior unchanged.
3. Keep repo-list and installation links GitHub-owned.

## Task 4: Tests

**Files:**

- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/tests/routes.test.mjs`

**Steps:**

1. Update the local setup assertions:
   - must match `npx codealmanac@latest setup`
   - must not match `almanac login`
   - must match browser sign-in/capture consent wording
   - must not match `local .almanac`
2. Add/adjust assertions that `/cli-login` uses `codealmanac login`.
3. Add/adjust assertions that the GitHub App install prompt names the `CodeAlmanac GitHub App`.

## Task 5: Verification And Docs

**Files:**

- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/verification-matrix.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/worklog.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/next-agent-brief.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/progress.md`

**Verification:**

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run test:routes
npm run test:frontend
npm run lint
npm run build
cd ..
git diff --check
```

Deploy after hosted commit:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
vercel deploy --prod --scope thealmanac --yes
curl -fsS -o /dev/null -w "%{http_code}\n" https://www.codealmanac.com
```
