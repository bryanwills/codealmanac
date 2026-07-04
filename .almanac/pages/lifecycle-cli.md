---
title: Lifecycle CLI
summary: The `codealmanac` CLI routes local wiki lifecycle work through foreground workflows, background lifecycle runs, and deterministic query/admin commands.
topics:
  - cli
  - flows
  - agents
sources:
  - id: root-parser
    type: file
    path: src/codealmanac/cli/parser/root.py
    note: Defines the public `codealmanac` program name and root command registration.
  - id: lifecycle-parser
    type: file
    path: src/codealmanac/cli/parser/lifecycle.py
    note: Defines public init, hidden sync, hidden worker, and hidden local-trigger command parsing.
  - id: dev-parser
    type: file
    path: src/codealmanac/cli/parser/dev.py
    note: Defines hidden developer ingest and garden lifecycle command parsing.
  - id: cloud-runs-parser
    type: file
    path: src/codealmanac/cli/parser/runs.py
    note: Defines cloud update-run commands with `run_id` arguments.
  - id: cloud-runs-dispatch
    type: file
    path: src/codealmanac/cli/dispatch/runs.py
    note: Dispatches cloud update-run commands to `app.workflows.cloud_runs`.
  - id: lifecycle-rendering
    type: file
    path: src/codealmanac/cli/render/lifecycle.py
    note: Renders foreground and background lifecycle results with run terminology.
  - id: cloud-runs-rendering
    type: file
    path: src/codealmanac/cli/render/cloud_runs.py
    note: Renders cloud update-run lists, details, logs, cancellation, and retry output.
  - id: wiki-parser
    type: file
    path: src/codealmanac/cli/parser/wiki.py
    note: Defines deterministic local wiki read, topic, health, reindex, serve, and tagging commands.
  - id: automation-parser
    type: file
    path: src/codealmanac/cli/parser/automation.py
    note: Defines local scheduled automation install, status, and uninstall commands.
status: active
verified: 2026-07-03
---

# Lifecycle CLI

The public program name is `codealmanac`. The CLI is an adapter over services and workflows: parsing builds request objects, dispatch calls the app composition root, renderers print results, and product behavior stays in workflows and services. [@root-parser]

[[lifecycle-architecture]] is the reading map for the surrounding workflow, harness, run ledger, and automation pages. [[process-manager-runs]] owns the repo-local lifecycle run ledger that background CLI commands create and the local viewer reads.

## Write-Capable Commands

`codealmanac init` initializes a local Almanac wiki. It accepts an optional path, configured root/name/description options, `--using`, foreground/background mode flags, `--force`, `--yes`, `--verbose`, `--guidance`, and background `--json`. Foreground init renders the finished run, wiki change count, and refreshed index summary; background init renders `run_id`, queued status, and worker PID. [@lifecycle-parser] [@lifecycle-rendering]

`codealmanac sync` is hidden but remains the scheduler-facing transcript sync entry point. Its status subcommand is read-only; its syncing path can queue lifecycle ingest runs and renders started work by `run_id`. [@lifecycle-parser] [@lifecycle-rendering]

`codealmanac dev ingest` and `codealmanac dev garden` are hidden developer surfaces for local ingest and garden workflows. They share lifecycle options such as `--wiki`, `--using`, foreground/background mode, `--title`, `--guidance`, and background `--json`. These commands are not evidence for adding public `absorb`, `build`, or `garden` aliases outside the current runtime. [@dev-parser]

The hidden worker command `codealmanac __run-worker` drains the repo-local lifecycle run queue. The hidden local-worker and local-trigger commands belong to branch-triggered local runs, not to the lifecycle run ledger. [@lifecycle-parser]

## Run Commands

`codealmanac runs list|start|show|cancel|retry|logs` is the cloud update-run surface. It dispatches to `app.workflows.cloud_runs`, renders `run_id`, and talks to the hosted API. [@cloud-runs-parser] [@cloud-runs-dispatch] [@cloud-runs-rendering]

`codealmanac local runs start|list|show|logs` is the local branch-triggered run surface. Repo-local lifecycle runs from init, ingest, garden, and sync are recorded by `app.runs` and read by `codealmanac serve` through `/api/runs`; there is no revived `jobs` command for them.

## Read And Organization Commands

`codealmanac search`, `show`, `topics`, `health`, `reindex`, `serve`, `tag`, `untag`, and `list` are deterministic local wiki commands. They may refresh derived index state or rewrite explicit metadata through organization verbs, but they do not invoke AI or write page prose. [@wiki-parser]

`codealmanac serve` starts the local read-only viewer. It reads wiki pages, index state, topics, backlinks, and lifecycle run data; it is not a lifecycle execution command.

## Automation Commands

`codealmanac automation install|status|uninstall` manages scheduled local sync and garden tasks. Automation owns scheduled invocation; it does not own transcript eligibility, lifecycle run storage, provider execution, or wiki-writing judgment. [@automation-parser]

## Boundary Rule

When adding CLI behavior, keep the CLI as an adapter. Public command names should express product intent, while internal naming follows the owning subsystem: repo-local lifecycle records, cloud executions, local trigger executions, and engine execution artifacts are all runs owned by their specific run domains. Query commands remain deterministic over committed wiki files plus derived local index state.
