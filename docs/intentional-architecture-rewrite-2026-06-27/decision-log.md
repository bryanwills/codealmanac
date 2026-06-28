# Intentional Architecture Rewrite Decision Log

Date: 2026-06-27
Branch: `codex/intentional-architecture-rewrite`

This file records durable rewrite decisions. Per-slice details stay in `worklog.md`; the target architecture stays in `rewrite-contract.md`.

## Decisions

### Rewrite by ownership, not by phases

The rewrite proceeds as production slices on `codex/intentional-architecture-rewrite`. Each slice leaves the branch buildable, testable, and committed. There is no phase gate separate from working code.

### Use file size as a smell, not a rule

Large files are reviewed for mixed ownership. Files are split when they have multiple reasons to change, not to satisfy an arbitrary line count.

### Edges own ambient runtime facts

CLI and process edges own facts such as argv, cwd, stdout capability, terminal sinks, stdin streams, stdin TTY capability, Node runtime version, worker entrypoints, process environment, and the current process id when it becomes persisted job state. Lower layers receive those facts through explicit contracts when they need them.

CLI edges also own process lifetime signals. Viewer/server code serves HTTP and exposes `close()`, while CLI command wiring waits for SIGINT/SIGTERM through an injected stop boundary.

Services do not own local process mechanics by default. When a service needs PID liveness or process signaling, the command or edge contract passes an explicit function so platform behavior stays at the boundary.

### Agent runtime provider registries are runtime-scoped

Claude and Codex agent runtime providers are created from an explicit runtime environment. Jobs and workers pass environment through the executor instead of importing singleton providers that close over `process.env`.

### Services own product decisions

Command adapters shape requests and render results. Services own workflow decisions, validation, coordination, and user-visible product semantics.

Command-private render modules own service-result-to-output branching. When a command receives a discriminated service result, the command should call the service and delegate the status-specific JSON/text/exit-code mapping to its render module instead of becoming a workflow decision layer.

### Stores and integrations stay mechanical

Stores own persistence mechanics. Provider adapters, process spawning, app-server protocols, launchd, npm, and OS behavior stay in integration-shaped modules unless they are product service contracts.

### Transcript discovery is platform, sync eligibility is service

Claude and Codex transcript-store scanning reads local provider files and normalizes raw JSONL shapes into typed transcript candidates. That belongs under `src/platform/transcripts/`. The sync service owns quiet-window eligibility, ledger reconciliation, cursor decisions, and Absorb handoff over those normalized candidates.

### Prefer explicit contracts over compatibility facades

Compatibility facades can remain only when callers still need a stable import. New code should depend on typed service, store, integration, or edge contracts with honest names.

### Guard boundaries with tests

Architecture-boundary tests are part of the rewrite, not decoration. When a smell is removed, add or update a test that makes the old leak harder to reintroduce.

### Keep the branch continuously releasable

Each meaningful slice should run focused verification, then broader lint/test/build/CLI smokes when risk warrants it. Commits should be pushed regularly to the rewrite branch.
