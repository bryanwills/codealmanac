# Product boundary notes

Date: 2026-06-27
Status: discussion record, not implementation plan

This note records the follow-up discussion after `README.md`. The README is the
primary synthesis. This file preserves the product boundary decisions, rejected
frames, and the conversation-capture implications so the next design pass does
not repeat the same confusion.

## The core confusion

The confusing question was:

```text
Is codealmanac local, hosted, an engine, a CLI, or a Modal runtime?
```

That question mixes five layers:

```text
artifact        .almanac/ committed in the repo
engine          the code wiki updater/searcher
CLI             the user-facing command surface
hosted product  teams, auth, GitHub App, billing, runs, source capture
worker runtime  Modal sandbox that runs the engine
```

The answer is not to split every layer into a separate product. The answer is
to keep the user story simple and keep internal seams honest.

## Product stance

`codealmanac` should be one open-core product.

```text
Free:
  your machine
  your keys
  your local checkout
  local reading
  optional local building

Paid:
  our hosted control plane
  our compute
  GitHub App automation
  team access
  run history
  source capture
  delivery back into the repo
```

Paid is not a smarter engine. Paid is less work, shared team state, hosted
compute, and access-controlled automation.

## Source of truth

For code wikis, hosted is not the source of truth.

```text
source of truth:
  .almanac/ files on the canonical branch

query/read layer:
  local index.db in a checkout
  hosted DB index for dashboard/search without a checkout

hosted control plane:
  decides and runs updates, then writes them back through git
```

This differs from the general `/almanac` product, where the hosted wiki can be
the canonical thing users pull from. CodeAlmanac is repo-native because the code
repo itself is branched, reviewed, and versioned.

Rule:

```text
default branch = published wiki
PR branch      = proposed wiki state
```

## CLI stance

Use one `codealmanac` CLI. Do not split into `almanac`, `codealmanac`, and
`usealmanac` for the same product.

The CLI should have postures:

```text
reader:
  read local .almanac/ files
  search/show/serve
  no login required

hosted:
  login
  connect repo/account
  inspect runs/repos
  install coding-agent capture hooks
  view captured sources

local lab:
  opt-in local execution
  init --local / build --local / sync / garden
  user machine, user keys, user commits
```

This keeps one product surface while making the trust boundary visible.

## Hosted features

Hosted should mean team orchestration around a repo-native wiki.

Hosted features:

```text
GitHub App installation
team and repo access control
billing and quotas
hosted update runs
Modal worker execution
PR/check/dashboard surfaces
run history and status
delivery policy
conversation/source capture
source attachment to runs
retention and deletion controls
hosted read index for dashboard users without a local checkout
```

Hosted should not mean:

```text
the .almanac/ files move out of git
local search/show proxy through hosted APIs
the OSS engine is crippled
the user must understand Modal or worker requests
```

## Local OSS features

The free/local path should remain real because trust matters.

Local features:

```text
read .almanac/
search/show/serve
create a local .almanac/ in lab mode
run local updates in lab mode
sync local coding-agent sessions in lab mode
write changes into the working tree by default
optionally auto-commit debounced/quarantined wiki commits
```

Local users pay with their own setup, model auth, compute, review, and
maintenance effort.

## Modal worker stance

Modal is not a user-facing CLI surface.

The worker should receive a resolved hosted run request:

```text
run id
repo checkout/workspace
operation
attached source references
delivery-independent settings
```

Then it runs the engine and returns a neutral result bundle.

The worker should not be designed around a human command such as:

```bash
codealmanac ingest github:pr:123 --sources ...
```

That shape leaks too much product meaning into a command string. It makes the
engine rediscover things the hosted backend already resolved, and it makes
conversation sources feel bolted on.

Better shape:

```text
hosted backend resolves policy and sources
worker checks out repo
worker prepares run input
engine receives one resolved request
engine writes .almanac/ changes
worker returns UpdateBundle
backend delivers
```

The exact engine entrypoint can still be a CLI for packaging reasons, but it
should be a machine entrypoint over a typed request, not the human workflow CLI.

## Conversation capture stance

Conversation capture belongs to the hosted posture unless the user explicitly
enables local lab capture.

Hosted capture:

```text
codealmanac login
codealmanac agents install
Codex/Claude Stop hook fires
hook command uploads transcript delta
server stores raw evidence and normalized events
later run attaches relevant source ids
worker receives attached source references
```

Capture does not start an update run by itself. It records source evidence.

Do not define "conversation" as the trigger. Provider sessions are resumable and
turn boundaries are clearer. The v1 capture boundary is provider turn stop.

## Rejected frames

Rejected: two product names for one code product.

```text
almanac = local
usealmanac = hosted
```

This makes the OSS and hosted tiers feel independent even though the hosted
product is paid CodeAlmanac.

Rejected: `almanac cloud`.

```text
almanac cloud login
```

This sounds like cloud is an add-on to a local product. The README's stronger
frame is one `codealmanac` CLI with capabilities unlocked by posture.

Rejected: hosted as canonical wiki store.

```text
hosted wiki replaces .almanac/
```

That is closer to the general `/almanac` product, not the code-repo product.

Rejected: per-turn hosted update runs.

```text
every captured coding-agent turn triggers a wiki update
```

This creates noisy runs, unclear delivery, privacy pressure, and repo-state
races. Capture and update should remain separate.

Rejected: source handoff as a magic committed-looking folder.

```text
.usealmanac/run/source-index.json
```

If the worker needs scratch files, keep them outside the repo checkout or make
their runtime-only nature impossible to confuse with `.almanac/`.

## Command sketch

Reader:

```bash
codealmanac search "checkout"
codealmanac show checkout-flow
codealmanac serve
```

Hosted:

```bash
codealmanac login
codealmanac whoami
codealmanac use <account-or-repo>
codealmanac repos
codealmanac runs
codealmanac agents install
codealmanac agents status
codealmanac sources list
```

Local lab:

```bash
codealmanac setup
codealmanac init --local
codealmanac sync --local
codealmanac garden --local
codealmanac build --local
```

The exact names can change. The important thing is that commands teach posture:
read, hosted, or local lab.

## Open decisions

Engine of record:

```text
TS engine today vs Python port later
```

Worker request shape:

```text
library call vs machine CLI command
typed request file vs stdin JSON
```

Local lab naming:

```text
--local flags vs lab namespace
```

Delivery defaults:

```text
PR branch
dedicated almanac/update branch
working tree
scheduled PR
direct commit when opted in
```

Capture visibility:

```text
owner-only raw transcript
team-visible existence/attachment
raw access grants
retention and delete semantics
```

## Short version

CodeAlmanac is not framework-vs-platform. It is open-core.

```text
same brand
same CLI
same engine
same .almanac/ artifact
different posture
```

The repo is the medium. Hosted writes. Local reads. Git is the handoff.

