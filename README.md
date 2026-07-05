# CodeAlmanac

CodeAlmanac is a local codebase wiki maintained by AI coding agents.

It keeps durable project knowledge next to the code: decisions, workflows,
invariants, incidents, gotchas, and context from real engineering sessions.
The wiki is markdown in your repository, backed by a local SQLite index for
fast search.

## Current Status

This Python rewrite is usable as a local alpha. It is not the old Node CLI and
it does not require a hosted service.

- Public command: `codealmanac`
- Repo wiki root: `almanac/` only
- Alternate repo wiki roots: none
- User state root: `~/.codealmanac/`
- Runtime: Python 3.12+
- Storage: local markdown plus derived state under `~/.codealmanac/`

## Install

From a published package:

```bash
uv tool install codealmanac
```

or:

```bash
python -m pip install codealmanac
```

From this checkout:

```bash
uv sync
uv run codealmanac --help
```

## Setup

Install global agent instructions for the local tools you use:

```bash
codealmanac setup --yes
codealmanac setup --yes --target codex
codealmanac setup --yes --target claude
```

Plain setup installs only local agent instructions and does not connect to a
hosted service. Scheduled automation is explicit:

```bash
codealmanac setup --yes --install-automation
codealmanac setup --yes --sync-every 5h --sync-quiet 45m
codealmanac setup --yes --install-automation --garden-off
```

`--install-automation` installs local scheduled `sync` and `garden` jobs.
Passing `--sync-every`, `--sync-quiet`, `--garden-every`, or `--garden-off`
also opts into automation installation.

To remove setup-owned instruction artifacts and scheduled automation:

```bash
codealmanac uninstall --yes
codealmanac uninstall --yes --keep-automation
```

## Quickstart

Inside a repository:

```bash
codealmanac init
codealmanac search "getting"
codealmanac show getting-started
codealmanac serve
```

`init` creates a local wiki scaffold under `almanac/`. CodeAlmanac does not
support alternate repo wiki roots.

## Daily Read Surface

Agents and humans use the same local read commands:

```bash
codealmanac search "checkout timeout"
codealmanac search --mentions src/checkout/
codealmanac show checkout-flow
codealmanac topics
codealmanac health
```

Use `--wiki <name>` to read another registered local wiki. By default,
commands resolve the nearest repository wiki from the current directory.

## Updating The Wiki

Lifecycle commands can ask a configured local agent harness to edit wiki pages.
They only allow source edits under `almanac/`.

```bash
codealmanac ingest README.md --using codex
codealmanac ingest github:pr:123 --using claude
codealmanac ingest README.md --using codex --background
codealmanac garden --using codex
codealmanac garden --using codex --background
```

`ingest` folds selected local material into the wiki. Inputs can include files,
directories, Git diffs, commit ranges, GitHub PRs or issues, URLs, and local
agent transcripts.

`garden` improves the existing wiki graph: stale pages, links, topics, weak
leads, duplicate pages, and unsupported claims.

No-op is valid. If the material adds no durable wiki knowledge, the harness
should leave the wiki unchanged.

Add `--background` to queue an `ingest` or `garden` run and start a detached
local worker. Plain `ingest` and `garden` run in the foreground.

## Sync And Automation

`sync` scans local Claude and Codex transcript stores, waits for quiet sessions,
and runs ordinary local ingest for eligible transcript ranges.

```bash
codealmanac sync status --from codex
codealmanac sync --from codex --using codex
codealmanac sync --from codex --using codex --background
codealmanac automation install sync --every 5h --quiet 30m
codealmanac automation status
```

Scheduled automation launches foreground `sync` or `garden` commands with
explicit unattended policy. It is local scheduler state, not cloud sync.
Use `sync --background` for manual queue-and-worker execution.

## Jobs

Lifecycle runs are recorded under `~/.codealmanac/`:

```bash
codealmanac jobs
codealmanac jobs show <run-id>
codealmanac jobs logs <run-id>
codealmanac jobs attach <run-id>
codealmanac jobs cancel <run-id>
```

Run logs include source-resolution facts, harness events, safety errors, and
terminal status.

## Providers

CodeAlmanac currently supports local Codex app-server and Claude Agent SDK
harnesses.

```bash
codex login
claude auth login
codealmanac doctor
```

Read commands do not need provider credentials. Write-capable lifecycle
commands need the selected harness to be available and authenticated.

## What Gets Created By Init

With the default root:

```text
your-repo/
|-- almanac/
|   |-- README.md
|   |-- topics.yaml
|   |-- architecture/
|   |   |-- README.md
|   |   `-- indexer.md
|   |-- decisions/
|   |   `-- local-first.md
|   `-- guides/
|       `-- setup.md
|-- src/
`-- ...
```

Markdown pages live directly under `almanac/` in meaningful folders.
`topics.yaml` organizes pages across folders. `README.md` files act as landing
pages for their folder routes.

For auto-detection, a repository counts as a CodeAlmanac wiki when
`almanac/topics.yaml` and `almanac/README.md` exist.

## Runtime State

Derived local state lives under `~/.codealmanac/`:

```text
~/.codealmanac/repos/<repo-id>/index.db
~/.codealmanac/repos/<repo-id>/runs/
```

Those runtime files are rebuildable local machine state. They do not belong in
the committed `almanac/` tree.

## Configuration

User config lives at:

```text
~/.codealmanac/config.toml
```

Project config lives at:

```text
almanac/config.toml
```

The first supported defaults are:

```toml
[harness]
default = "codex"

[sync]
quiet = "30m"
```

CLI flags still win over config.

## Local Viewer

```bash
codealmanac serve
```

The viewer is read-only. It renders pages, search, topics, backlinks, and
file-reference navigation from local wiki data. By default it can switch across
available registered local wikis. Use `codealmanac serve --wiki <name>` to
narrow the viewer to one wiki.

## Public Contract

This rewrite is local-only for now.

- No hosted login/connect/upload commands.
- No public SDK or MCP package.
- No compatibility aliases.
- No alternate wiki roots.
- No hidden cloud write path.
- No second wiki command name.

Hosted integration can be added later around the same repo-owned wiki artifact,
but it is not part of this release surface.
