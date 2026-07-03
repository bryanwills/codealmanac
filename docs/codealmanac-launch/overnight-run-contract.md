# Overnight Run Contract

Status: active.
Date: 2026-07-03.

This file records the execution order for the long autonomous launch run.

## Operating Authority

This launch has no external customer compatibility constraint. If a database
shape, migration history, URL, package name, CLI command, frontend route, or
code organization choice is wrong for the launch product, change it instead of
protecting it.

Use provider-owned concepts where they exist:

- WorkOS owns human identity, AuthKit sessions, and any WorkOS-backed machine
  credentials.
- GitHub owns accounts, installations, repositories, branches, pull requests,
  commits, and webhook event shapes.
- Supabase/Postgres owns CodeAlmanac product state, but not identity.
- Vercel, Render, GitHub Actions, PyPI, Doppler, PostHog, Autumn, and provider
  CLIs/APIs should be used directly where they are the real control plane.

Do not invent parallel product-owned systems unless a provider gap forces a
small named adapter.

## Priority Order

The run has two large halves:

1. Build the product spine until CLI, API, frontend, backend, and deployables
   work together.
2. Sharpen the codebase so it reads like it was designed after the product
   model became clear.

The first major objective remains infrastructure and deployment, before deep
product implementation.

Order:

1. Verify provider CLIs and auth state.
2. Prepare a clean `codealmanac-hosted` rename workspace.
3. Rename/move `usealmanac` to `codealmanac-hosted` under `AlmanacCode`.
4. Update repository names, package names, remotes, and provider settings.
5. Deploy the cloud app/backend so there is a real deployed target.
6. Set up or repair Vercel, Render, Modal, Supabase, GitHub App, Doppler,
   PostHog, and Autumn state as needed.
7. Run deployment smoke checks.
8. Only then continue into larger functionality chunks.

The intended wake-up state is: there is something deployed, not only a local
refactor.

## Product Spine

Finish the concrete product path first:

- root `codealmanac setup` is cloud setup, not local automation setup
- CLI setup/login use the final WorkOS-backed auth contract through
  CodeAlmanac API endpoints
- API exposes the nouns the frontend and CLI actually need
- hosted repo list, repo setup, repo settings, trigger policy, delivery policy,
  and runs surfaces work in production
- GitHub App webhooks create or update parent records before child records
- PR/merge events on maintained branches create runs
- delivery defaults to commit and is configurable per maintained branch
- run records and run events are stored with the same conceptual shape in cloud
  and local, even when persistence differs
- CLI, frontend, backend, and migrations are deployed after coherent chunks

## Codebase Sharpening

After the spine works, the run should spend serious time improving code quality.
This is not cosmetic cleanup. The goal is that a new engineer or agent can read
the names and infer the product.

Allowed and encouraged:

- reorganize packages and folders around stable product/provider domains
- rename services, stores, DTOs, routes, and tables to match GitHub, WorkOS, and
  CodeAlmanac nouns
- collapse, rewrite, or repair Supabase migrations because launch has no
  external users
- remove stale local/cloud split-brain
- remove compatibility husks once callers have moved
- simplify DTOs and API names so frontend, CLI, API, and core use the same
  vocabulary
- break large files by responsibility
- introduce a consistent project-wide error/result approach if current error
  handling is scattered
- add architecture tests when boundaries become important enough to protect
- mirror cloud/local concepts only where the parallel is real

Do not refactor for motion. Every reorganization should make one of these true:

- a product noun has one obvious home
- a provider boundary stops leaking raw provider details
- a future SDK/API method becomes easier to name
- a test can enforce an architectural rule
- deleted code removes a real source of confusion

## README And Install UX

Restore the old README's feel rather than replacing it with a new marketing
document. Keep the original banner, cadence, and most of the language where it
still describes the product correctly. Update only the launch facts and command
surface.

Public install should prefer a product-grade one-liner:

```bash
curl -fsSL https://codealmanac.com/install.sh | sh
codealmanac setup
```

The install script can use `uv tool install` internally. Keep the manual path in
docs for transparency:

```bash
uv tool install --python 3.12 codealmanac
codealmanac setup
```

Do not reintroduce npm/npx instructions for the Python CLI.

## Provider CLI Check

Initial local CLI availability:

```text
gh        present
vercel    present
render    present
supabase  present
modal     present
doppler   present
atmn      available through frontend npm context
posthog   available through npm package investigation, not on PATH
autumn    no separate binary found; use atmn
```

Missing standalone CLIs do not automatically block the run. Use project npm
scripts, provider APIs, or dashboards when those are the correct interface.

Follow-up findings:

```text
cd /Users/rohan/Desktop/Projects/usealmanac/frontend
npm exec -- atmn --version
  -> 1.1.8

npm exec -- atmn --help
  -> works; commands include env, push, pull, preview, dashboard, login

npm exec --package @posthog/cli -- posthog-cli --help
  -> works; commands include login, sourcemap, api

npm exec --package @posthog/cli -- posthog-cli --version
  -> failed locally with spawnSync Unknown system error -88
```

Provider docs confirm:

- Autumn's JavaScript monorepo ships `atmn` as the CLI.
- PostHog documents `@posthog/cli` as the CLI package and `posthog-cli` as the
  binary.
- PostHog also documents `npx @posthog/wizard`, but the local Node 21.7.3
  runtime failed that wizard with an ESM directory-import error. Use Node 20.20+
  or Node 22.22+ if the wizard is needed.

## Implementation Cadence

The run should not spend the night on tiny commit ceremony.

Preferred cadence:

```text
plan a coherent chunk
implement the chunk
refactor while the shape is fresh
run focused checks
run broader checks at chunk boundaries
commit and push the coherent chunk
update steering docs
continue
```

Do not test every two-minute edit. Do test before committing/pushing each
meaningful chunk and before claiming a deployed state.

## Functionality Versus Slow Development

The launch run has two pressures:

- ship working functionality
- preserve the long-term architecture

The compromise is not to skip architecture. The compromise is to use larger
functional slices:

```text
infrastructure deployed
cloud onboarding path works
repo setup path works
trigger/delivery config exists
worker uses engine contract
run history is visible
local setup/update path works
```

Refactors are allowed inside these chunks when they make the chunk fit cleanly.
Refactors that do not affect the launch path should wait.

## Testing And Evidence

Test as much as possible. Prefer real provider/browser verification at the end
of coherent chunks, not only unit tests.

Maintain a running testing record in `worklog.md` or `verification-matrix.md`
with:

- what was tested
- exact command or provider surface used
- production or local URL when relevant
- result
- commit/deploy/run id when relevant
- anything not testable without user action

At minimum, keep checking:

- full Python tests and lint for `codealmanac`
- hosted route/frontend/backend tests where touched
- browser login/setup/repo/settings flows in production
- backend health and relevant API endpoints
- GitHub webhook behavior or replayed webhook payloads
- PyPI install and `codealmanac setup` smoke after CLI releases
- Vercel and Render deploy status after provider changes

If blocked, record the block instead of silently skipping the surface. The
wake-up handoff should say exactly what remains human-testable.

## Supabase

No external customers are using the product yet. Supabase migrations can be
rewritten, collapsed, repaired, or reset when that is the cleanest path.

Still record the chosen migration action in `worklog.md` and verify the final
schema against the launch requirements.
