# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, push, and RelayForge update.

## Last Completed Slice

Slice 41 converged hosted product identity and provider deployment naming.

Implemented:

- hosted worktree at
  `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
- hosted branch `codex/workos-authkit-api-foundation`
- active hosted identity strings now say `codealmanac-hosted` in agent docs,
  FastAPI metadata, loggers, domain-event session keys, frontend support
  defaults, and the clean-slate Supabase migration comment
- Vercel project id `prj_sBOdSIF82roDGnkFeYrh5qdg6epp` was renamed from
  `thealmanac/usealmanac` to `thealmanac/codealmanac-hosted`
- clean hosted frontend checkout was linked to the renamed Vercel project
- hosted commit `a781e51 chore: align hosted product identity` was pushed
- Vercel production deployed
  `https://codealmanac-hosted-lasush9ur-thealmanac.vercel.app` and aliased it
  to `https://www.codealmanac.com`
- Render service `srv-d8g8nb37uimc739vnnsg` deployed exact commit
  `a781e5189da4403bcf8b31d7fb9129b3779aec01`; deploy
  `dep-d938j4km0tmc73d6p3sg` is live
- production smoke passed for `https://www.codealmanac.com` and
  `https://codealmanac-backend-docker.onrender.com/api/health`

Verified:

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_events_contract.py tests/test_identity_auth_contract.py tests/test_architecture_contract.py -q
uv run ruff check .
uv run python -m compileall src modal_app -q
uv run pytest -q
git diff --check
cd ../frontend
npm run test:routes
npm run test:frontend
npm run lint
npm run build
```

Counts so far: hosted backend focused `85 passed`; hosted backend full
`334 passed, 1 warning`; frontend routes `27 passed`; frontend components
`44 passed`; hosted ruff, compileall, lint, build, and diff-check passed.

## Next Pressure Test

Choose the next launch-hardening slice between terminal run fanout,
cloud run cancel/retry semantics, richer frontend onboarding pages, and
remaining provider cleanup.

Pressure points:

- terminal failed/stale runs still do not have a dedicated `RunFailed` or
  `RunStale` GitHub Check subscriber
- CLI commands list/show/log/start cloud runs, but do not cancel/retry them
- `runs cancel` needs a real Modal/provider cancellation primitive before it
  should be public
- `runs retry` needs an explicit failed/stale source-head policy
- browser setup/onboarding entrypoints now have stable redirect URLs, but
  richer onboarding screens still need product UI
- old inline-message conversation routes should remain compatibility-only
- old Modal app `usealmanac-updates` is still deployed; retire it only in an
  explicit provider cleanup step
- dirty `/Users/rohan/Desktop/Projects/usealmanac` still exists and should not
  be used for launch work until cleaned or renamed

## Known Repo State

The CodeAlmanac branch is `dev`. Slice 31 is pushed to `origin/dev` at
`f20e928d feat: expose maintenance package api`; Slice 36 is pushed to
origin at `8ca50e0f feat: mirror cloud repository triggers in CLI`; Slice 37
is pushed to origin at `bc177cf2 feat: inspect cloud runs from CLI`; Slice 38
is pushed to origin at `117b36db feat: open cloud pages from CLI`; Slice 39
is pushed to origin at `0e3879e1 feat: start cloud runs from CLI`.

The hosted auth branch is
`/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
on `codex/workos-authkit-api-foundation`. Slice 27 is pushed to origin at
`c91e162 feat: add v1 CLI auth routes`; Slice 28 is pushed to origin at
`36211ba feat: add capture credential API`; Slice 29 is pushed to origin at
`5644a65 feat: add capture transcript upload`; Slice 30 is pushed to origin at
`191d8d8 feat: materialize capture source refs`; Slice 31 is pushed to origin
at `51c2cb2 feat: call codealmanac maintenance api`; Slice 32 is pushed to
origin at `12cfc08 feat: persist hosted run events`; Slice 33 is pushed to
origin at `9098b65 feat: record stale delivery outcomes`; Slice 34 is pushed
to origin at `4e4c94b feat: expose run event timeline`; Slice 35 is pushed to
origin at `1b00b63 feat: add repository trigger policies`; Slice 36 is pushed
to origin at `fbf8b5a feat: add CLI repository trigger routes`; Slice 37 is
pushed to origin at `168f9b2 feat: add CLI run read routes`; Slice 38 is
pushed to origin at `ed7e765 feat: add cloud route handoff`; Slice 39 is
pushed to origin at `14caf8b feat: start cloud runs from CLI`; Slice 40 is
pushed to origin at `8795849 feat: emit terminal run events`; Slice 41 is
pushed to origin at `a781e51 chore: align hosted product identity`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
