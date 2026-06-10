# Architecture Audit Worklog

## 2026-06-08 Initial Setup

User goal: perform a deep, critical architecture audit of CodeAlmanac without
changing source code. The user explicitly wants the audit to question whether
existing behavior deserves to exist, not merely assume every special case has a
hidden legitimate reason.

Process constraints from repo instructions:

- `MANUAL.md` says the unit of work is evolving the codebase so the feature fits,
  and refusal is valid when the feature or mechanism is not worth its
  architectural cost.
- `MANUAL.md` distinguishes seams from machinery: build names, boundaries, and
  contracts early; defer speculative implementations, dispatchers, and broad
  frameworks until concrete cases exist.
- `.almanac/README.md` says wiki pages should preserve non-obvious knowledge
  that helps future agents; the wiki is dense factual project memory, not a
  generic reference library.
- `accidental-special-case-architecture` is directly relevant. It says this
  codebase has a known risk of AI-added one-off mechanisms: special paths,
  copied files, workflow-only storage, provider-specific conditionals outside
  provider modules, prompt-specific preprocessing, helper scripts, and parallel
  lifecycle paths.
- `lifecycle-architecture` states the main lifecycle boundaries: operations own
  wiki semantics, process manager owns execution lifecycle and run observability,
  harness providers own runtime execution truth, and automation owns scheduled
  invocation of known tasks.
- `provider-lifecycle-boundary` documents a prior cleanup target: separate
  provider identity/config, runtime adapters, readiness/auth/model-choice status,
  instruction installation, and external transcript discovery.
- `harness-providers` documents that `AgentRunSpec` is the provider-neutral
  execution contract and that provider adapters must reject unsupported fields
  rather than pretend capabilities exist.

Initial hypothesis to test against code: the main risk is not that every module
is bad. The main risk is that some lifecycle boundaries may be documented but
not consistently visible from the directory structure, names, command adapters,
and feature-level ownership.

## Open Questions

- Are command files thin adapters, or do they still own domain behavior?
- Are lifecycle operations, capture discovery, automation, and process-manager
  responsibilities cleanly separated in current source?
- Are provider boundaries still crisp after later Codex app-server work?
- Are there features whose product value no longer justifies their code shape?
- Are names simple enough for a small open-source tool, or do they encode
  enterprise-style abstractions that hide simple behavior?

## 2026-06-08 Source Inspection Pass 1

The top-level directory structure is better than the user's suspicion might
imply. Most major nouns have homes: `wiki`, `operations`, `process`, `harness`,
`agent`, `capture`, `platform`, `viewer`, `config`, `connectors`, and `ingest`.

The clearest architectural smell so far is `src/cli/sqlite-free.ts`. The
underlying need is legitimate: setup/update/doctor/uninstall must work when the
native SQLite binding is broken. The implementation is still ugly because it
duplicates Commander parsing in a hand-written pre-router. A cleaner shape would
make command registration lazy enough that non-SQLite commands can use Commander
without importing SQLite-dependent modules.

The second clear smell is duplicated capture discovery. Manual capture still
uses `src/capture/input.ts`, which can auto-resolve only Claude sessions and
rejects `--all-apps` and non-Claude app discovery. Scheduled capture uses
`src/capture/discovery/*`, which already knows Claude and Codex. The target
should be one discovery module with different selection policies.

The third clear issue is documentation drift. Repo docs still say normal CLI
commands do not write page content, but current edit commands intentionally
rewrite page frontmatter. This can be legitimate if the invariant is narrowed to
"deterministic metadata edits only; lifecycle agents own prose writes." The
current wording is misleading.

Provider boundaries are mostly cleaner than expected. Runtime provider adapters
live under `src/harness/providers`; readiness/auth/model-choice status lives
under `src/agent/readiness` and `src/agent/auth`; config provider ids live under
`src/config/providers`. The split is documented and mostly followed. The
remaining smell is naming: `AgentProviderId` and `HarnessProviderId` duplicate
the same ids under different lifecycle names.

The process manager is strong overall but imports operation report semantics.
That is a smaller ownership leak: operation-specific structured output
summarization probably should not be hardwired inside process lifecycle code.

## 2026-06-08 Subagent Integration

All four independent reports were written under
`docs/architecture-audit-2026-06-08/reports/`.

Converged conclusions:

- The broad architecture is better than the smell level implied. The correct
  target is boundary cleanup, not a wholesale folder rewrite.
- The lifecycle path needs typed start APIs so internal callers do not parse CLI
  output.
- Capture transcript discovery should be one source model with different manual
  and scheduled selection policies.
- Provider runtime execution and readiness/status should stay split, but shared
  provider identity/defaults should not be duplicated.
- `AgentRunSpec.connectors` and persisted raw Codex display payloads are stale
  or accidental runtime surface.
- `src/wiki/query/` is underpowered and should absorb duplicated CLI/viewer SQL.
- `almanac serve` is currently a local console, not only a wiki viewer.
- The repo invariant should say "no hidden AI and no page-prose writes outside
  lifecycle operations" rather than "normal CLI never reads/writes page
  content."
- Local GitHub source access needs a product decision: local `gh`, Composio, or
  explicitly separate surfaces.

New synthesis files:

- `subagent-briefs.md`
- `target-architecture.md`
- `refactor-roadmap.md`
- `completion-audit.md`
