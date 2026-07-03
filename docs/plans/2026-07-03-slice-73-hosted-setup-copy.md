# Slice 73: Hosted setup copy follows the public CLI

## Goal

Make the production hosted onboarding pages describe the public `codealmanac` CLI contract that shipped in `0.1.5`.

## Problem

Chrome verification on `https://www.codealmanac.com/setup` showed stale product copy:

- `codealmanac setup` is described as asking before installing Claude/Codex capture.
- Dashboard banners say setup chooses whether capture should be installed.
- Route tests currently enforce that stale wording.

The actual CLI contract is:

```text
codealmanac setup
  -> cloud login
  -> global Codex/Claude instruction files
  -> no capture hooks

codealmanac capture enable
  -> explicit cloud conversation capture hooks
```

## Scope

- Update hosted frontend setup/onboarding copy.
- Update repository readiness copy where empty capture state points users to the wrong command.
- Update route/component tests so stale setup/capture wording cannot re-land.
- Verify frontend tests, lint/build as needed, production Chrome behavior after deploy.

## Out of Scope

- No backend schema/API changes.
- No CLI changes in this slice.
- No new onboarding mechanics.

## Design

The frontend should mirror the CLI one-to-one:

```text
/setup
  shows install + setup as the machine setup step
  says setup signs in and installs agent instructions
  links to CLI guide

/dashboard/local-agent-access
  shows setup first
  shows capture enable as the explicit optional next command

repository readiness
  empty capture means run codealmanac capture enable
```

This is copy and contract repair, not a new abstraction.

## Files

- `frontend/src/app/setup/page.tsx`
- `frontend/src/app/dashboard/local-agent-access/page.tsx`
- `frontend/src/components/shell/local-agent-access-banner.tsx`
- `frontend/src/components/repositories/setup-summary.tsx`
- `frontend/tests/routes.test.mjs`
- `frontend/tests/frontend/repository-setup-summary.test.tsx`

## Verification

- `cd frontend && npm run test:routes`
- `cd frontend && npm run test:frontend`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- Production Chrome check on `/setup` after deploy.
