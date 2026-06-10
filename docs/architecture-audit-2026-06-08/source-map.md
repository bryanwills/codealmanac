# Source Map

## Top-Level Shape

CodeAlmanac is a TypeScript ESM CLI with three broad surfaces:

- Query and edit commands over a local `.almanac/` wiki.
- Lifecycle operations that run AI agents against wiki source.
- Platform/setup support for local installation, automation, provider readiness,
  config, updates, and agent instruction files.

The current source tree mostly has honest top-level names:

- `src/wiki/`: markdown/wiki graph indexing, query helpers, health checks,
  registry, and topics.
- `src/operations/`: Build, Absorb, Garden operation spec creation and process
  start delegation.
- `src/process/`: durable run records, logs, snapshots, queue/lock behavior, and
  foreground/background process execution.
- `src/harness/`: provider-neutral run spec, events, final output, tools, and
  runtime provider adapters.
- `src/agent/`: agent-support lifecycles: prompts, readiness, auth, instruction
  installation.
- `src/capture/`: transcript discovery, sweep eligibility, cursor ledger, and
  repo locks.
- `src/platform/`: launchd automation, install-time launcher/runtime behavior,
  and package self-update.
- `src/viewer/`: local web viewer API/server/static assets and run-log
  projections.
- `src/connectors/` and `src/ingest/`: external source references and Composio
  GitHub source inspection.

## Entry And CLI Registration

`bin/codealmanac.ts` runs the SQLite ABI guard before importing `src/cli.ts`.
The guard skips setup/version/update-like paths so users can repair an install
even when `better-sqlite3` is broken.

`src/cli.ts` owns invocation-level behavior: internal update worker,
background run worker, update nags, setup shortcut routing, SQLite-free command
fast paths, Commander construction, grouped help, and parse.

`src/cli/register-commands.ts` delegates command registration to four files:

- `register-query-commands.ts`
- `register-edit-commands.ts`
- `register-wiki-lifecycle-commands.ts`
- `register-setup-commands.ts`

This registration split is readable, but it still imports command modules
eagerly within each registration file. That eager import is why
`src/cli/sqlite-free.ts` exists as a separate pre-Commander parser for commands
that must run without loading SQLite-dependent modules.

## Lifecycle Flow

Lifecycle command flow:

```text
Commander action
  -> src/cli/commands/operations.ts
  -> src/operations/{build,absorb,garden}.ts
  -> src/operations/run.ts
  -> src/process/{background,manager}.ts
  -> src/harness/providers/*
```

`src/operations/run.ts` is the central spec builder. It loads base prompts plus
operation prompts, adds runtime/source-control context, requests read/write/edit
search/shell tools, sets max turns, marks provider sessions ephemeral, and
stores operation metadata.

`src/process/manager.ts` centralizes foreground/queued execution, run records,
event logging, page snapshots, page-change summaries, provider session id
persistence, successful-run reindexing, and cancellation finalization.

The process layer currently imports `operations/reports.ts` to parse structured
operation output into run summaries. This is a possible ownership leak: process
records need durable observability, but the semantic contract
`almanac_operation_report_v1` belongs to operations.

## Capture Flow

Manual capture uses `src/capture/input.ts` from
`src/cli/commands/operations.ts`. It resolves explicit transcript files and can
auto-discover Claude transcripts, but it reports `--all-apps` and non-Claude app
auto-discovery as not implemented.

Scheduled capture uses `src/capture/discovery/*` plus `src/capture/sweep.ts`.
That path discovers Claude and Codex session candidates, checks quiet windows,
skips internal Almanac provider sessions, guards ledger cursors with prefix
hashes, starts background captures, and reconciles pending ledger entries with
process run records.

The scheduled path is more complete than the manual path. That split is a
candidate for consolidation.

## Provider And Agent Support

Runtime providers live under `src/harness/providers/` and implement
`HarnessProvider`.

Readiness providers live under `src/agent/readiness/providers/` and implement
`AgentProvider` for setup/status/model choices.

Config-owned provider ids live in `src/config/providers.ts`. Runtime-owned
provider ids live in `src/harness/types.ts`.

This matches the documented split in broad strokes, but the names still make
the code feel like it has two provider systems:

- `AgentProviderId` versus `HarnessProviderId`
- `AgentProvider` versus `HarnessProvider`
- `AGENT_PROVIDER_METADATA` versus `HARNESS_PROVIDER_METADATA`

The split may be correct; the naming probably needs to be plainer.

## Wiki Query And Viewer

`src/wiki/indexer/index.ts` is large but has a coherent purpose: parse page
files into SQLite graph tables and FTS rows. Query commands call
`ensureFreshIndex()` before reading.

`src/wiki/query/search.ts` owns reusable search query builders, including FTS
term builders and file-mention filter construction.

`src/wiki/query/page-view.ts` owns the reusable page projection for `show` and
viewer page detail.

`src/viewer/api.ts` uses `getPageView()` and low-level search helpers, but it
also owns its own SQL for overview, topic pages, search, file mentions, and page
summaries. This is not automatically wrong because viewer is a separate product
surface, but it is duplicate query projection logic that may drift from CLI
search/show behavior.

## Setup And Platform

`src/cli/commands/setup/index.ts` has been split into workflow steps, which is
good. Setup still directly imports Claude readiness types and Codex instruction
exports for compatibility and tests, which keeps setup provider-adjacent even
after provider lifecycle cleanup.

`src/cli/commands/automation.ts` is an application command module that plans
known launchd tasks and delegates plist mechanics to `src/platform/automation/`.
The current automation task catalog is explicit: capture, garden, update.

`src/platform/install/global.ts`, `src/platform/install/launcher-runtime.ts`,
and `src/abi-guard.ts` exist because native SQLite and temporary `npx` installs
create real install-time failure modes. The need is legitimate; the CLI
workarounds around that need should still be simplified.
