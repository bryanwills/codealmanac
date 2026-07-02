# Slice 55: Cloud Setup Checklist

Status: implemented.
Date: 2026-07-02.

## Scope

Make the hosted `/setup` page read as the launch onboarding hub for cloud
CodeAlmanac.

This slice covers:

- show an ordered setup checklist on `/setup`
- keep GitHub App installation as the first browser-owned step
- show connected GitHub accounts from the real `/me` DTO
- point users to repository access, repository settings, and the CLI setup
  guide without inventing repository/capture state on the top-level page
- keep the install command Python/PyPI-shaped:
  `uv tool install codealmanac` then `codealmanac setup`
- preserve GitHub-only auth copy; no email/password/magic-link/setup-local copy
- add route and component tests that pin this cloud setup contract

This slice does not cover:

- signed-in production walkthrough; that still needs an authenticated browser
  session
- PyPI publishing; blocked by PyPI `invalid-publisher`
- backend API changes
- GitHub App dashboard changes
- changing repository settings semantics

## Design

The page should feel like:

```text
/setup
  Step 1: Sign in with GitHub       # already done by route guard/session
  Step 2: Install GitHub App        # browser/GitHub-owned, CTA if missing
  Step 3: Choose repositories       # GitHub installation settings per account
  Step 4: Configure repo automation # dashboard repo settings
  Step 5: Set up this machine       # CLI setup, capture consent happens there
```

The top-level setup page can show step completion only for facts already present
in `MeDTO`: signed-in user, connected accounts, account installation ids, and
repository selection. It must not claim repository count, branch policy status,
or capture status because those are repository-specific facts fetched on the
repository settings page.

## Files

Hosted repo:

- `frontend/src/app/setup/page.tsx`
- `frontend/tests/routes.test.mjs`
- focused component test if the setup checklist is extracted

CodeAlmanac launch docs:

- `docs/codealmanac-launch/next-agent-brief.md`
- `docs/codealmanac-launch/progress.md`
- `docs/codealmanac-launch/verification-matrix.md`
- `docs/codealmanac-launch/worklog.md`

## Verification

Hosted:

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run test:routes
npm run test:frontend
npm run lint
npm run build
```

If `npm run build` needs provider environment unavailable locally, record the
exact blocker and run the strongest focused route/frontend gates.

CodeAlmanac docs:

```text
git diff --check
```

## Result

Hosted `/setup` now shows a real ordered cloud setup checklist:

```text
Sign in with GitHub
Install the GitHub App
Choose repositories
Configure repository automation
Set up this machine
```

The page still renders only facts already available through `MeDTO`: session
presence, connected accounts, installation ids, and repository selection. It
does not invent repository count, branch policy state, or capture state on the
top-level setup page.

Verification passed:

```text
frontend npm run test:routes -> 27 passed
frontend npm run test:frontend -> 52 passed
frontend npm run lint
frontend npm run build
browser-harness http://localhost:3000/setup unauthenticated gate
```

The full local dev stack did not start because `codealmanac/dev_personal`
Doppler is missing `GITHUB_TOKEN_ENCRYPTION_KEYS`. The frontend-only browser
check proved unauthenticated `/setup` reaches the GitHub-only login surface;
signed-in setup walkthrough remains open until a backend env with that key is
available.
