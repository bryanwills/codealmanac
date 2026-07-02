# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, push, and RelayForge update.

## Last Completed Slice

Slice 44 added real cloud run cancellation and exposed it through the
CodeAlmanac CLI.

Implemented:

- hosted worktree at
  `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
- hosted branch `codex/workos-authkit-api-foundation`
- hosted backend has `RunStatus.CANCELLED`, `UpdateCancellation`,
  `Updates.cancel_run(...)`, and `POST /v1/runs/{run_id}/cancel`
- browser backend has `POST /api/runs/{run_id}/cancel`
- Modal cancellation uses the stored `worker_call_id` through
  `modal.FunctionCall.from_id(call_id).cancel(terminate_containers=False)`
- terminal `RunCancelled` events publish GitHub Checks with conclusion
  `cancelled`
- hosted frontend DTOs, status metadata, and BFF gateway accept `cancelled`
  runs
- CodeAlmanac has `codealmanac runs cancel <run-id>`

Verified:

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest -q
uv run ruff check .
uv run python -m compileall src modal_app -q

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run test:routes
npm run test:frontend
npm run lint
npm run build

cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest -q
uv run ruff check .
uv run python -m compileall src -q
```

Counts so far: hosted backend `348 passed, 1 warning`; frontend routes
`27 passed`; frontend components `44 passed`; CodeAlmanac `496 passed`.
Frontend build retained the known CSS optimizer warning about `m-* utility`.

## Next Pressure Test

Choose the next launch-hardening slice between cloud run retry semantics,
richer repository setup UI, and remaining provider cleanup.

Pressure points:

- `runs retry` needs an explicit failed/stale source-head policy
- browser setup/onboarding entrypoints now have stable redirect URLs and setup
  copy, but richer repository setup UI still needs product design
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
is pushed to origin at `0e3879e1 feat: start cloud runs from CLI`. Slice 44 is
implemented locally and should be committed/pushed as the current slice.

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
pushed to origin at `a781e51 chore: align hosted product identity`; Slice 42 is
pushed to origin at `97564f7 feat: publish terminal run checks`; Slice 43 is
pushed to origin at `eafe60c feat: align cloud setup copy`. Slice 44 is
implemented locally and should be committed/pushed as the current slice.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
