# Slice 53: Hosted Main Convergence

Status: implemented.
Date: 2026-07-02.

## Scope

Converge `codealmanac-hosted` `main` with the verified
`codex/workos-authkit-api-foundation` branch and record production smoke
evidence.

This slice covers:

- verify the hosted branch before moving `main`
- fast-forward hosted `main` to the current verified branch commit
- verify hosted remote refs after push
- smoke public production URLs that should remain stable
- update launch progress, worklog, verification matrix, and next-agent brief

This slice does not cover:

- Vercel deployment; the hosted diff from `main` is test-only
- Render deployment; the backend code is unchanged
- signed-in browser verification
- PyPI publishing

## Design

The hosted branch currently differs from `origin/main` only in route-test
guardrails. Converging `main` is still useful because provider branch tracking
and future release work should not depend on a stale feature branch.

No production deploy is required for test-only changes. The production smoke
checks prove the existing deployed public frontend and backend are still
reachable:

```text
https://www.codealmanac.com
https://www.codealmanac.com/login
https://codealmanac-backend-docker.onrender.com/api/health
```

## Files

Hosted worktree:

- no file changes expected

CodeAlmanac repo:

- `docs/codealmanac-launch/next-agent-brief.md`
- `docs/codealmanac-launch/progress.md`
- `docs/codealmanac-launch/verification-matrix.md`
- `docs/codealmanac-launch/worklog.md`

## Verification

Hosted:

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run test:routes
npm run lint
```

Remote refs and production smoke:

```text
git push origin HEAD:main
git ls-remote origin codex/workos-authkit-api-foundation main
curl -I https://www.codealmanac.com
curl -I https://www.codealmanac.com/login
curl -fsS https://codealmanac-backend-docker.onrender.com/api/health
```

CodeAlmanac docs:

```text
git diff --check
```
