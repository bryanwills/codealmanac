# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, and push.

## Last Completed Slice

Slice 25 converged the hosted baseline for the `codealmanac-hosted` rename.

Implemented:

- clean hosted worktree at
  `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
- hosted branch `codex/hosted-baseline-convergence`
- current `origin/main` baseline with hosted conversation-sync work preserved
- hosted rename/deploy-surface commit
  `1d237db chore: rename hosted deploy surfaces`
- CodeAlmanac-hosted package/deploy defaults in backend, frontend, Modal
  runtime defaults, and deploy workflow files

Verified:

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pytest tests/test_modal_worker_contract.py

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run test:routes
npm run test:frontend
npm run build
```

## Next Pressure Test

The next substantial slice should start the WorkOS/AuthKit and public API
foundation in `codealmanac-hosted`.

Use the hosted convergence branch/worktree as the clean base, or merge that
branch first and start from updated hosted main.

Before coding, write the next slice plan under `docs/plans/`, then implement
the full slice, update this brief, update `progress.md`, send a RelayForge
progress update, commit, and push.

## Known Repo State

The CodeAlmanac branch is `dev`. Slice 24 implementation commit `38423978` and
bookkeeping commit `d9a55b9e` are pushed to `origin/dev`.

The hosted convergence branch is
`/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
on `codex/hosted-baseline-convergence`, pushed to origin at commit `1d237db`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
