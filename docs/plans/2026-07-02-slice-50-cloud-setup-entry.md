# Slice 50: Cloud Setup Entry

Status: implemented; hosted deploy requested.
Date: 2026-07-02.

## Scope

Finish the browser setup entry point that the CLI and website can both send
users to.

This slice covers:

- add `/setup` as the cloud setup hub
- keep `/setup/repo` as the repo-specific resolver
- show sign-in, GitHub App, repository, and local capture steps from the browser
- reuse existing WorkOS, GitHub App, account, repository, and capture surfaces
- add route tests for the new setup entry

This slice does not cover:

- API rate limits
- Supabase migrations
- new backend services

Deployment was added after implementation because production sign-in was
blocked by Vercel configuration.

## Design

`/setup` is a Server Component. It reads the current WorkOS-backed session
through `getMe()`. If the user is not signed in, the existing API helper
redirects to `/login?next=/setup`.

If no GitHub App installation exists, `/setup` renders the same account-level
GitHub App CTA as the dashboard. If accounts exist, it shows connected accounts,
repository access, and the next browser/CLI actions.

The page should not duplicate repository settings. It should route users into
the existing account/repository pages.

## Files

Hosted worktree:

- `frontend/src/app/setup/page.tsx`
- `frontend/src/lib/routes.ts`
- `frontend/src/proxy.ts`
- `frontend/tests/routes.test.mjs`

CodeAlmanac repo:

- `docs/codealmanac-launch/frontend-surface-contract.md`
- `docs/codealmanac-launch/worklog.md`
- `docs/codealmanac-launch/next-agent-brief.md`
- `docs/codealmanac-launch/progress.md`

## Verification

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run test:routes
npm run lint
npm run backend:smoke
```

Run a build if the route test or lint touches route resolution behavior.

Actual verification:

```text
npm run test:routes
npm run lint
npm run build
```

## Deployment Notes

Vercel production was missing the required WorkOS AuthKit environment
variables, which caused `/login` and `/dashboard` to return 500s. Added
`WORKOS_API_KEY`, `WORKOS_CLIENT_ID`, `WORKOS_COOKIE_PASSWORD`, and
`NEXT_PUBLIC_WORKOS_REDIRECT_URI` to Vercel Production, Development, and
Preview branch `dev`.

Render backend logs did not show auth-path 500s or error-level failures in the
checked window.
