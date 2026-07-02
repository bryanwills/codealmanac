# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, and push.

## Last Completed Slice

Slice 27 implemented cloud CLI auth over the hosted WorkOS/AuthKit foundation.

Implemented:

- hosted worktree at
  `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
- hosted branch `codex/workos-authkit-api-foundation`
- hosted `/v1` CLI auth aliases over the existing CLI token service:
  `/v1/auth/cli/start`, `/v1/auth/cli/sessions/{session_id}`,
  `/v1/auth/cli/sessions/{session_id}/complete`,
  `/v1/auth/cli/sessions/{session_id}/poll`, `/v1/me`, and
  `/v1/auth/logout`
- legacy `/api/cli/...` routes preserved for dashboard compatibility
- `codealmanac` cloud auth state, HTTP client, store, browser opener port, and
  browser login workflow
- public cloud identity commands: `codealmanac login`,
  `codealmanac whoami`, and `codealmanac logout`
- cloud-first `codealmanac setup`; local setup remains
  `codealmanac local setup`
- local CLI auth state stored at `~/.codealmanac/auth.json` mode `0600` with
  only the issued hosted CLI token

Verified:

```text
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest -q
uv run ruff check .
uv run ruff format --check .

cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest -q
uv run ruff check .
git diff --check
uv run codealmanac login --help
uv run codealmanac setup --help
uv run codealmanac whoami --help
uv run codealmanac logout --help
```

Counts: hosted backend `289 passed, 1 warning`; codealmanac `474 passed`.

## Next Pressure Test

The next substantial slice should either:

- implement capture installation/status/repair and the narrow capture
  credential flow, or
- build hosted repo/run API parity: repositories, branch trigger policy, SQL
  `runs`, `run_events`, bundle/result storage by reference, and delivery state.

Before coding, write the next slice plan under `docs/plans/`, then implement
the full slice, update this brief, update `progress.md`, send a RelayForge
progress update, commit, and push.

## Known Repo State

The CodeAlmanac branch is `dev`. Slice 27 is implemented locally and should be
pushed to `origin/dev` after final documentation commit.

The hosted auth branch is
`/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`
on `codex/workos-authkit-api-foundation`. Slice 27 is implemented locally and
should be pushed to origin after final documentation commit.

Slice 25 hosted convergence branch `codex/hosted-baseline-convergence` is
pushed to origin at commit `1d237db`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
