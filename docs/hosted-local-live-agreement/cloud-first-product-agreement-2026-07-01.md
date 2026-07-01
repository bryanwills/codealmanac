# Cloud-First Product Agreement

Date: 2026-07-01.
Status: active product agreement.

## Decision

Cloud is the default CodeAlmanac product experience.

Most users should be guided into:

```text
install CLI
connect/login to cloud
install GitHub App
choose repos/environments
install agent/source capture hooks when needed
inspect runs and wiki in cloud dashboard
read the committed wiki locally through the CLI
```

Local remains real, but it is opt-in:

```text
almanac setup --local
almanac update --local
almanac runs --local
almanac agents install --local
```

The CLI may support `--cloud`, but cloud is the default where a command can
talk to cloud.

## Why Cloud Default

Cloud is the best UX because it owns the hard work:

- GitHub App installation
- repo/account/team state
- environment/branch triggers
- source collection from coding-agent sessions
- background workers
- model/container credentials
- run history
- PR or commit delivery
- billing and quotas
- dashboard reader and activity surface

Local asks the user to own setup, credentials, source capture, scheduling,
delivery, and troubleshooting. That is valuable for trust and free use, but it
should not be the primary first-run product story.

## CLI Stance

The CLI is still important, but not all CLI commands should mean local.

Recommended default:

```text
read commands:
  local by nature, because the wiki files are in the repo checkout

setup / connect / runs / repos / agents / sources:
  cloud by default

update/build/garden-style execution:
  cloud by default once connected
  local only with --local or local-specific setup
```

Examples:

```bash
almanac search "auth"           # local repo wiki read
almanac show auth-flow          # local repo wiki read

almanac setup                   # cloud walkthrough
almanac setup --local           # local-only setup

almanac runs                    # cloud runs by default
almanac runs --local            # local run ledger

almanac agents install          # install cloud source-capture hooks
almanac agents install --local  # install local-lab capture hooks
```

If a command can materially change user data or remote state, its output should
make the posture visible:

```text
Posture: cloud
Repo: github.com/org/repo
Environment: main
Delivery: pull request
```

## Separate Install Command

Basic CLI installation should not silently install capture hooks or automation.

Separate commands should exist for setup actions:

```text
almanac setup
  cloud walkthrough: login, GitHub App, repo selection, environment defaults

almanac agents install
  installs coding-agent capture hooks for cloud source collection

almanac setup --local
  creates/configures local repo wiki and local state only

almanac agents install --local
  installs local-lab capture hooks only if local capture is supported
```

The reason: installing hooks changes privacy and source-capture behavior. It
deserves an explicit command and a clear explanation.

## No SDK Or MCP For Now

Do not plan around SDK or MCP in this phase.

The active product surfaces are:

- CLI
- cloud dashboard
- GitHub App
- worker/container

MCP can become useful later for agent-native reads/actions. SDK can become
useful later for third-party integrations. Neither should shape the current
cloud/local product decision.

## What Local Is For

Local exists for:

- open-source trust
- users who refuse cloud access to code/conversations
- offline/private use
- contributors who want to inspect and modify the engine
- debugging and development of the core engine
- a free path that proves the artifact is not locked in cloud

Local is not the default UX and should not force the cloud product to copy every
local behavior.

## Product Boundary

Cloud is paid for:

- managed compute
- automatic updates
- team state
- source collection
- delivery
- dashboard/run history
- billing-aware quotas

Local is free for:

- repo-local reading
- optional manual/local update workflows
- local inspection and contribution

Cloud should not be marketed as a smarter engine. It is less work, better
coordination, and managed operation.

