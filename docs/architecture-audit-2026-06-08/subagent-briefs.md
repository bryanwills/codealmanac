# Subagent Briefs

Date: 2026-06-08

This file records the independent reports used by the architecture audit. The
reports are inputs, not automatic decisions. The final target shape is in
`target-architecture.md`.

## Lifecycle Command Boundaries

Report: `reports/lifecycle-command-boundaries.md`

Scope: `src/cli`, `src/operations`, `src/process`, `src/capture`,
`src/platform/automation`, and `src/ingest`.

Main conclusions:

- The operation -> process manager -> harness shape is correct and should stay.
- `capture sweep` currently recovers run ids by parsing rendered capture command
  stdout. That is a high-severity boundary leak.
- Manual capture and scheduled sweep use divergent transcript discovery paths.
- GitHub ingest has two competing source-access models: local `gh` guidance and
  Composio-backed `source github` tooling.
- `src/cli/commands/operations.ts` is too thick and has become the place where
  lifecycle edge cases accumulate.
- `src/cli/sqlite-free.ts` protects a real recovery need but duplicates too much
  command parsing.
- Scheduled Garden by default is a product question. Its cost and surprise are
  higher than scheduled capture.

Architecture implication:

The lifecycle surface needs typed use-case entrypoints below Commander. Command
files should render results; sweep/setup/internal callers should consume typed
results directly.

## Provider, Harness, Config, Readiness, Connectors

Report: `reports/provider-harness-boundaries.md`

Scope: `src/agent`, `src/harness`, `src/config`, `src/connectors`,
provider-adjacent command code, process log surfaces, and provider tests.

Main conclusions:

- Runtime harness providers and readiness/status providers are correctly split.
  They should not be merged into one provider mega-layer.
- Provider identity/default facts are duplicated across config, harness,
  readiness, setup, process spec validation, and records.
- `AgentRunSpec.connectors` is stale harness machinery. Current production
  network access is already represented by `networkAccess`.
- Normalized tool display events still persist nested raw Codex protocol payloads.
- Readiness view parses provider prose instead of receiving structured status.
- Doctor has a parallel injected provider-status path instead of using the same
  readiness catalog.
- Codex legacy exec compatibility is still exported even though the app-server
  path is the production runtime.

Architecture implication:

Keep the runtime/readiness split, but introduce one small provider identity
catalog and remove stale runtime fields. Provider adapters should normalize raw
transport data before it reaches durable run logs or viewer projections.

## Wiki Storage And Query Boundaries

Report: `reports/wiki-storage-query-boundaries.md`

Scope: `src/wiki`, `src/viewer`, and CLI command boundaries for read,
organization, and maintenance commands.

Main conclusions:

- The indexer/storage core is coherent. `src/wiki/indexer/` has a real single
  job: project markdown into SQLite graph/search tables.
- The literal "pure query" invariant is false. Read commands can read markdown,
  refresh `index.db`, auto-register repos, and some explicit organization
  commands rewrite metadata.
- `src/wiki/query/` is too small for the current product. CLI and viewer code
  duplicate page, topic, file-mention, and summary SQL.
- `src/viewer/api.ts` is a local Almanac console, not only a current-repo wiki
  viewer. It exposes wiki, jobs, review, connection, and global registry data.
- Health is starting to mix diagnosis with source cleanup and deterministic fix
  behavior.

Architecture implication:

The invariant should be narrowed to "no AI and no page-prose writes outside
lifecycle operations." Shared page/topic read models should move into
`src/wiki/query/`, and viewer API modules should be split by surface.

## Prior-Art Patterns

Report: `reports/prior-art-patterns.md`

Scope: outside architecture patterns and how they should or should not apply to
CodeAlmanac.

Main conclusions:

- Ports and adapters is useful as a dependency rule, not as a folder-renaming
  exercise.
- Functional core / imperative shell is useful locally for policy decisions,
  cursor evaluation, provider event mapping, and viewer projections.
- A lightweight service-layer/use-case boundary is useful for command files
  that have grown too much policy.
- Static registries are enough for providers and scheduled tasks. There is no
  evidence for plugin loaders, command buses, daemon frameworks, or enterprise
  Clean Architecture rings.
- SQLite should remain a generated local read model, not the wiki source of
  truth.
- The viewer should remain a local adapter over shared query models.

Architecture implication:

Keep concrete product vocabulary. Add small named seams only where two or more
surfaces already need the same product behavior.

