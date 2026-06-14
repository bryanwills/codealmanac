# Target Architecture

Date: 2026-06-08

## Overall Verdict

The codebase is not globally misshapen. The top-level vocabulary is mostly
honest: `wiki`, `operations`, `process`, `harness`, `capture`, `agent`,
`platform`, `viewer`, `config`, `connectors`, and `ingest` are real product
areas. The operation -> process manager -> harness provider flow is a good
center of gravity. The indexer is also a coherent subsystem.

The ugly parts are not from the broad folder structure. They come from local
exceptions that stayed after their original slice moved on:

- a hand-written sqlite-free CLI router beside Commander;
- capture start state flowing through rendered stdout;
- two transcript discovery models for one product noun;
- duplicated provider identity/default catalogs;
- stale connector runtime fields inside the provider-neutral run spec;
- raw Codex protocol payloads leaking into durable normalized logs;
- viewer and CLI read-model SQL drifting because `src/wiki/query/` is too thin;
- docs that describe a stricter invariant than the code actually follows;
- Composio and local `gh` GitHub ingest paths competing for product truth.

The correct refactor is not a wholesale `domain/application/adapters` rewrite.
It is a sequence of small boundary corrections that make current product nouns
true again.

## Target Mental Model

```text
CLI / viewer / scheduler
  -> small named use-case functions
    -> operation specs, capture policy, ingest resolution, query read models
      -> filesystem, SQLite, provider runtimes, launchd, external tools
```

Concrete directories should stay concrete:

```text
src/cli/commands/          parse flags and render command results
src/viewer/                local HTTP adapter and viewer payload assembly
src/operations/            Build / Absorb / Garden spec construction
src/capture/               session discovery, capture start, sweep policy, ledger
src/ingest/                source-ref parsing, source resolution, source context
src/process/               run lifecycle, queue, records, logs, snapshots
src/harness/               provider-neutral runtime spec and provider adapters
src/agent/                 readiness, auth, prompts, global instruction files
src/wiki/indexer/          markdown -> SQLite projection
src/wiki/query/            shared read models for CLI and viewer
src/wiki/topics/           topic storage, DAG rules, frontmatter rewrites
src/wiki/health/           report composition over wiki integrity checks
src/platform/automation/   scheduler task catalog and OS scheduler adapter
src/platform/install/      global install and launcher runtime mechanics
src/platform/update/       update check/install/notifier state
src/config/                TOML schema, codec, store, origins
```

The important rule is dependency direction, not folder purity. Command files and
viewer routes may know UI/output shape. Provider adapters may know provider
protocols. The process manager may know run lifecycle. Inner policy modules
should not know Commander objects, rendered stdout, provider JSON-RPC payloads,
or launchd plist details.

## Boundaries To Preserve

### Operation specs are the right lifecycle boundary

`src/operations/run.ts` builds provider-neutral `AgentRunSpec` values and keeps
Build, Absorb, and Garden out of provider protocol details. Keep that shape.
Future lifecycle behavior should extend operation spec construction rather than
bypass it from command files.

### Process manager owns durable run lifecycle

`src/process/` is the right owner for queued/background execution, foreground
single-writer behavior, records, logs, snapshots, cancellation, page-change
summaries, and reindex-on-success. Do not move observability into provider
transcripts or command output.

The one ownership leak is semantic operation-output parsing inside
`src/process/manager.ts`. The manager should call a neutral summary projection
provided by the operation spec or operation module, not import a concrete
`almanac_operation_report_v1` parser directly.

### Runtime providers and readiness providers should stay split

Runtime execution lives under `src/harness/providers/`. Setup/status/model
readiness lives under `src/agent/readiness/`. That split is correct.

The refactor should remove duplicated identity facts, not merge the two
lifecycles. A small shared provider identity module is enough:

```text
src/providers.ts
  ProviderId
  PROVIDERS
  isProviderId()
  providerDisplayName()
```

Runtime capability metadata can remain in `src/harness/providers/metadata.ts`.
Readiness can add executable/status/model-choice behavior. Setup can consume the
same identity/default labels instead of hard-coding them again.

### SQLite index remains a generated read model

`.almanac/pages/`, `.almanac/topics.yaml`, `.almanac/review.yaml`, and
`.almanac/runs/` remain the inspectable local artifacts. `index.db` remains
derived and disposable. The indexer can stay large if it keeps that single job.

The missing piece is a fuller read-model layer under `src/wiki/query/`.

## Boundaries To Fix

### 1. Replace command stdout coupling with typed lifecycle start APIs

`capture sweep` should not parse `runCaptureCommand()` output to find a run id.
The target is a typed start function that both CLI and sweep can use.

Preferred simple shape:

```text
src/capture/start.ts
  startCaptureRun(options) -> CaptureStartResult

src/ingest/start.ts
  startIngestRun(options) -> IngestStartResult
```

The CLI wrappers render those results. Sweep consumes `CaptureStartResult`
directly. Ingest-specific report output and source-specific runtime options move
with ingest, not into `src/cli/commands/operations.ts`.

Do not add a command bus. Exported functions are enough.

### 2. Collapse transcript discovery to one source model

Manual capture and scheduled sweep should consume the same candidate model:

```text
src/capture/discovery/
  claude.ts
  codex.ts
  index.ts
  types.ts
```

Manual capture can choose the latest matching candidate. Sweep can choose every
quiet eligible candidate. Those are selection policies over the same discovery
data, not separate scanners.

Manual `capture --app codex` should either work through this model or the flag
should disappear until it works.

### 3. Make sqlite-free recovery a Commander import problem, not a second CLI

The need is legitimate: setup, doctor, update, uninstall, and automation repair
commands must work when `better-sqlite3` cannot load.

The current solution is ugly: `src/cli/sqlite-free.ts` mirrors command parsing.

Target:

- Register command shapes without importing SQLite-heavy implementations.
- Lazy-import command implementations inside action handlers.
- Keep the early ABI guard in `bin/codealmanac.ts`.
- Keep only the truly pre-Commander setup shortcut if Commander import itself
  cannot be made safe.

If that cannot be done cleanly in one pass, shrink `sqlite-free.ts` to a small
documented recovery surface rather than mirroring setup and automation flags.

### 4. Tighten provider data contracts

Provider cleanup should do four things:

- Replace duplicated provider id/default/display facts with one small identity
  catalog.
- Rename readiness provider types so they do not look like runtime providers.
  `ReadinessProvider` is clearer than `AgentProvider`.
- Remove `AgentRunSpec.connectors` unless a production runtime truly consumes
  connector identity. Keep `networkAccess` or a neutral runtime requirement.
- Remove nested `display.raw` from persisted harness events. If thread/turn ids
  are useful, normalize them as first-class fields.

Readiness should return structured status data such as `readiness`,
`accountLabel`, `installFix`, and `loginFix`. The readiness view should not
parse provider prose.

### 5. Expand `src/wiki/query/`

The viewer and CLI need shared read models:

```text
src/wiki/query/pages.ts
  PagePreview
  recentPages()
  pagesBySlug()
  searchPages()
  pagesMentioningPath()

src/wiki/query/topics.ts
  topicSummaries()
  topicDetail()
  pagesDirectlyTagged()
  pagesForSubtree()
```

`src/wiki/query/search.ts` can keep FTS expression builders. CLI and viewer can
still choose different FTS expressions, but pagination, archive filters, topic
attachment, path mention semantics, and summary shapes should not be duplicated.

### 6. Admit that `almanac serve` is a local console or scope it down

Current `src/viewer/api.ts` is not only a current-repo wiki viewer. It exposes
global registry browsing, jobs, review decisions, connector status, and wiki
graph data.

There are two coherent choices:

- Keep the global local console and rename docs/help accordingly.
- Scope `serve` to the current wiki and move global console behavior behind a
  different command or flag.

The product already seems closer to "local Almanac console." If that is the
choice, split implementation modules:

```text
src/viewer/wiki-api.ts
src/viewer/jobs-api.ts
src/viewer/review-api.ts
src/viewer/connections-api.ts
src/viewer/global-api.ts
src/viewer/server.ts
```

Also warn or document clearly when binding beyond localhost because the exposed
data is broader than a rendered wiki page.

### 7. Move health repair/source parsing out of the health index

`src/wiki/health/index.ts` should compose health reports. Source/citation
checks and deterministic legacy source-frontmatter repair should live in a
source maintenance module.

Target:

```text
src/wiki/sources/health.ts
src/wiki/sources/maintenance.ts
src/wiki/health/index.ts
```

Keep `health --fix` narrow. Do not let health become a general wiki-editing
surface.

## Product Decisions To Make Before Refactoring

### GitHub source access

The current tree contains both local `gh` ingest guidance and Composio-backed
GitHub source commands. That is the clearest product-level split.

Recommended decision: keep local GitHub ingest on `gh` for the local OSS CLI,
and treat Composio as an experimental connector/source-tool surface unless a
current product requirement needs it. Hosted GitHub maintenance should not be
forced through the local Composio shape; the wiki already points toward GitHub
App/MCP or native GitHub tooling for hosted jobs.

If Composio stays:

- keep it out of `AgentRunSpec` until runtime adapters actually consume it;
- make it a source-tool boundary, not provider runtime identity;
- remove stale wiki/docs claims that ingest currently uses Composio if tests and
  source still use local `gh`.

If Composio does not stay:

- remove `connect github`, `source github`, connector config fields, viewer
  connections payloads, and stale runtime connector tests in one intentional
  slice.

### Scheduled Garden default

Scheduled capture has a strong correctness reason: quiet agent sessions become
eligible evidence. Scheduled Garden is broader and more expensive. It asks an
agent to reshape the graph every few hours by default.

Recommended decision: make setup default to capture-only unless Garden has a
clear trigger policy such as accumulated page changes, health issues, or an
explicit user opt-in.

### Deprecated aliases

The repo still carries deprecated paths such as `almanac ps`, `capture status`,
`show --raw`, and old `almanac set` forms.

Recommended decision: choose either a real removal window or declare them
permanent compatibility. The current half-state keeps tests and parser branches
alive without saying why.

## Invariant Rewrite

The current invariant says normal CLI commands never read or write page content.
That is too broad.

Recommended wording:

> Only lifecycle operations invoke AI or write page prose. Read commands may
> refresh derived local index state and read committed markdown for display or
> validation. Organization commands may deterministically rewrite wiki metadata
> through explicit verbs such as `tag`, `topics`, `review`, and `health --fix`.

That wording matches the code and keeps the important safety line: no hidden AI
and no hidden page-prose writes.

## What Not To Do

- Do not rename the repo into `domain/`, `application/`, `ports`, and
  `adapters`.
- Do not add a command bus, class-per-command framework, or plugin loader.
- Do not wrap every filesystem or SQLite call in generic repositories.
- Do not make the viewer a source of truth.
- Do not move run records into SQLite just because they are queryable.
- Do not keep compatibility shims merely because tests import them.
- Do not preserve one-off product paths without choosing whether they are real
  features.

