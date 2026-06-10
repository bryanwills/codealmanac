# Prior-Art Patterns For The CodeAlmanac Architecture Audit

Date: 2026-06-08

This report translates outside architecture patterns into recommendations for CodeAlmanac. It is not a pattern catalog. The useful question is which seams should be first-class in a small local TypeScript CLI, and which "architecture" would create enterprise ceremony without buying anything.

## Executive Synthesis

CodeAlmanac already has the right broad shape for a local-first CLI with AI maintenance jobs: CLI/viewer/scheduler are driving adapters; Build, Absorb, Garden, capture sweep, query/read models, and process-manager runs are application behavior; provider runtimes, SQLite, filesystem state, launchd, npm install/update, and connector transports are driven adapters.

The audit should not recommend a new top-level `ports/`, `adapters/`, `domain/`, or `application/` rewrite. Prior art supports the inside/outside dependency rule, but CodeAlmanac is small enough that abstract folder names would hide the actual product vocabulary. Keep concrete subsystem names: `operations`, `capture`, `process`, `harness`, `wiki/indexer`, `wiki/query`, `platform/automation`, `viewer`, `config`, and `cli`.

The main refactor target is command-adapter thickness. `src/cli/commands/operations.ts` is mostly an adapter, but it also resolves capture/ingest inputs, chooses source-specific GitHub PR report output, resolves providers, renders lifecycle results, and maps operation errors. That is a bounded smell: do not split it into a command-bus framework, but do move source-specific operation construction toward `src/ingest/` or `src/operations/` once a second source-specific output contract appears.

The strongest prior-art-backed anti-recommendation is: do not add enterprise Clean Architecture machinery. No generic `IRepository` layer for every filesystem read. No `CommandBus`/`Handler` class per CLI action. No plugin loader for providers until users can actually install third-party providers. No daemon framework for scheduled jobs. No full CQRS/event-sourcing layer around a wiki whose source of truth is markdown plus a generated SQLite index.

## 1. Ports And Adapters: Borrow The Boundary, Not The Diagram

[Alistair Cockburn's original hexagonal architecture article](https://alistair.cockburn.us/hexagonal-architecture) says the application should be usable without its final UI or database and should be driven by users, tests, batch scripts, or programs through ports. The point for CodeAlmanac is not hexagon-shaped folders; it is avoiding product logic leaking into UI, SQLite, provider SDK, and scheduler code.

Concrete mapping for CodeAlmanac:

| Pattern role | CodeAlmanac fit | Recommendation |
|---|---|---|
| Driving adapters | `src/cli/commands/`, `src/viewer/`, scheduled `almanac capture sweep` / `garden` invocations | Keep them thin: parse input, call named application behavior, render output. |
| Application/use cases | `src/operations/`, `src/capture/sweep.ts`, `src/process/manager.ts`, `src/wiki/query/` | Keep product semantics here: Build/Absorb/Garden, quiet-session eligibility, run lifecycle, query projections. |
| Driven adapters | `src/harness/providers/`, `src/platform/automation/`, `src/wiki/indexer/`, filesystem stores, connector transports | Keep technology details here: Claude/Codex protocols, launchd plist shape, SQLite DDL, JSON/TOML codecs. |

Cockburn also warns that "how many ports" is a taste call and tends to favor a small number of natural ports, not one port per use case. CodeAlmanac should follow that. The natural ports are roughly:

- Lifecycle execution: `AgentRunSpec` to harness providers.
- Local persistence/projection: markdown/wiki files to SQLite and run records.
- Scheduler wakeup: automation tasks to OS-specific schedulers.
- Source intake: transcript/file/source references to Absorb context.
- Query presentation: CLI and viewer read-model calls.

Anti-recommendations:

- Do not create `src/ports/ProviderPort.ts`, `src/adapters/CodexAdapter.ts`, etc. The existing `src/harness/types.ts` and `src/harness/providers/` names are more honest.
- Do not wrap every `better-sqlite3` statement in a generic repository. SQLite is already a concrete local projection mechanism; the seam is "wiki query model", not "any database someday".
- Do not let operations import provider SDK types, launchd plist details, or viewer route details. That is where the dependency rule matters.

## 2. Clean Architecture: The Dependency Rule Is Useful; The Rings Are Optional

[Robert C. Martin's Clean Architecture article](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) states the dependency rule: source dependencies point inward, and outer data formats should not leak inward. It describes use cases as application-specific rules that orchestrate data flow, with interface adapters converting between external and internal formats.

Concrete CodeAlmanac translation:

- `src/operations/run.ts` is a good inner boundary: it builds provider-neutral `AgentRunSpec` values and leaves process execution to `src/process/`.
- `src/harness/providers/codex/*` and `src/harness/providers/claude.ts` should continue to decode raw provider protocol fields once and emit normalized `HarnessEvent` / `HarnessResult` values.
- `src/viewer/jobs.ts` should not know provider app-server notification shapes; it should read process-manager events and derive display projections.
- `src/capture/discovery/` should normalize Claude/Codex transcript stores into `SessionCandidate` before sweep policy runs.

Current fit from source inspection:

- `src/harness/providers/index.ts` uses a small static provider registry. That is appropriate.
- `src/platform/automation/tasks.ts` uses a small static scheduled-task catalog. That is appropriate.
- `src/viewer/api.ts` delegates page views to `src/wiki/query/page-view.ts` and job storage to `src/viewer/jobs.ts` / `src/process/index.ts`. That is the right direction.
- `src/cli/commands/operations.ts` still mixes source-specific ingest behavior with command rendering. It is not catastrophic, but it is the best candidate for "adapter got too smart".

Anti-recommendation: do not import Clean Architecture's vocabulary wholesale. "Entity", "Interactor", "Presenter", and "Gateway" would be less clear than CodeAlmanac's existing product terms. The test is whether a fresh agent can tell what changes when the file changes.

## 3. Functional Core, Imperative Shell: Use It Locally

The [Functional Core, Imperative Shell](https://functional-architecture.org/functional_core_imperative_shell/) pattern separates pure decision logic from I/O orchestration. For CodeAlmanac, this is more useful than a global class/layer architecture because many subsystems are effect-heavy by nature: filesystem scans, SQLite, child processes, launchd, and provider streams.

Good CodeAlmanac targets for pure cores:

- Path and link normalization: already in `src/wiki/indexer/paths.ts`, `src/wiki/query/search.ts`, and `src/wiki/indexer/wikilinks.ts`.
- Capture cursor decisions: `evaluateCaptureCursor()` and prefix-hash logic in `src/capture/sweep.ts` are close to the ideal.
- Ledger reconciliation decisions: keep "what state should this session move to?" separate from "write `.almanac/runs/capture-ledger.json`".
- Job display projection: `src/viewer/job-projections.ts` is the right place for pure "events to display model" logic.
- Provider notification mapping: Codex app-server event mapping should stay mostly pure after JSON-RPC reading has happened.

Anti-recommendations:

- Do not pretend `process/manager.ts` can be pure. It is the unit of work around spawned jobs, records, logs, snapshots, cancellation, and reindexing.
- Do not split every helper into pure/impure pairs. Apply the pattern where decisions are complex enough to test without touching OS state.
- Do not hide I/O behind mocks when a focused temp-home integration test is clearer.

## 4. Service Layer / Use-Case Boundary: Keep Exported Functions, Not A Command Bus

[Fowler's Service Layer](https://martinfowler.com/eaaCatalog/serviceLayer.html) defines an application boundary and coordinates responses for operations. [Cosmic Python's service-layer chapter](https://www.cosmicpython.com/book/chapter_04_service_layer.html) gives a pragmatic version: API/CLI code calls a service layer, which orchestrates domain and persistence abstractions. Its [Unit of Work chapter](https://www.cosmicpython.com/book/chapter_06_uow.html) frames atomic persistence as one entrypoint for a workflow.

CodeAlmanac should keep a lightweight function-oriented version:

```ts
// Driving adapter
runCaptureCommand(parsedFlags) -> CommandResult

// Use case / application behavior
resolveCaptureTranscripts(...)
runAbsorbOperation(...)
runOperationProcess(...)

// Driven adapters
startBackgroundProcess(...)
getHarnessProvider(provider).run(...)
writeRunRecord(...)
```

This pattern says command files should not own multi-step product policy. It does not require `CaptureCommandHandler`, `AbsorbInteractor`, or a `CommandBus`.

Concrete recommendations:

- Keep public command functions as exported functions returning `CommandResult`.
- Move reusable command-neutral selection logic out of command files when it has a product name. Example: source-specific report output for GitHub PR ingest should live with source ingest or Absorb operation construction, not inside CLI rendering.
- Keep `src/process/manager.ts` as the unit-of-work boundary for lifecycle runs. It owns the atomic-ish sequence: create/run record, log events, execute provider, snapshot pages, finalize status, reindex on success.
- If setup, automation, or connect workflows grow, split by named workflow step as the repo already does under `src/cli/commands/setup/`; do not introduce a generic workflow engine.

## 5. Command/Query Separation And CQRS: CodeAlmanac Already Has The Useful Part

[Fowler's Command Query Separation note](https://martinfowler.com/bliki/CommandQuerySeparation.html) separates state-changing commands from side-effect-free queries. His [CQRS note](https://martinfowler.com/bliki/CQRS.html) is also a warning: separate command/query models are valuable in some complex domains but add risky complexity when applied broadly.

CodeAlmanac's useful read/write separation is already present:

- Markdown pages, topics, review YAML, config, and run records are source files.
- `.almanac/index.db` is a generated read projection.
- `src/wiki/query/` is shared by CLI query commands and the viewer.
- `src/viewer/` is read-only except implicit reindex and connector status reads.
- Lifecycle write commands go through `src/process/` and the operation queue.

Recommendations:

- Keep query commands and viewer APIs on shared query modules. If duplicated SQL appears in `src/cli/commands/show.ts` and `src/viewer/api.ts`, extract to `src/wiki/query/` or `src/process/query` rather than viewer-specific helpers.
- Keep SQLite as a projection, not as the canonical wiki document store.
- Preserve the CLI contract that query commands are deterministic and AI-free.

Anti-recommendations:

- Do not adopt full CQRS terminology or event-sourcing machinery.
- Do not build an event bus for wiki changes unless a real second consumer requires it.
- Do not move `.almanac/runs/*.json` into SQLite just because CQRS examples use databases. Run files are inspectable local audit artifacts; SQLite is useful when query complexity or indexing justifies it.

## 6. Adapter Registries: Static Catalogs Are Enough

[Fowler's Registry](https://martinfowler.com/eaaCatalog/registry.html) is a well-known lookup object for common services. CodeAlmanac has two good small registries:

- `src/harness/providers/index.ts`: `claude`, `codex`, `cursor`.
- `src/platform/automation/tasks.ts`: `capture`, `garden`, `update`.

These are not service locators in the harmful sense because they are typed, static, and close to the boundary they select. They are better than spreading `if (provider === "codex")` across command and operation code.

Recommendations:

- Keep provider metadata and provider execution capability truth under `src/harness/providers/`, not setup/readiness modules.
- Keep scheduled task definitions explicit. Three tasks do not justify a plugin system.
- Add registries only at axes with at least two real implementations and a stable typed contract.
- If source ingest grows beyond GitHub PRs, consider a source-ref resolver catalog under `src/ingest/`, but keep it static until users can install external source plugins.

Anti-recommendations:

- No dynamic provider/plugin autoloading yet.
- No global mutable registry shared across unrelated subsystems.
- No "adapter registry" that hides dependency direction; registries should be called from adapters/application shells, not from inner pure decision code.

## 7. Local-First CLI Structure: Local Files Are The Product Contract

[Ink & Switch's local-first essay](https://www.inkandswitch.com/essay/local-first/) emphasizes local ownership, optional networks, preservation, privacy, and user control. CodeAlmanac is local-only rather than collaborative local-first, but the architecture lesson still applies: the user's repository and home directory are the durable system, not a hosted service.

[SQLite's "Appropriate Uses" page](https://www.sqlite.org/whentouse.html) says SQLite emphasizes economy, efficiency, reliability, independence, and simplicity for local application storage. That fits `.almanac/index.db` as a local generated index. [SQLite WAL docs](https://www.sqlite.org/wal.html) support the current WAL choice for read concurrency, while reminding the audit that local DB files have operational constraints.

[npm package.json docs](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/) support the current package-level discipline: explicit `bin`, explicit `files`, and bundled runtime assets. The viewer and prompts being shipped in `files` is architecture, not packaging trivia.

Recommendations:

- Treat `.almanac/pages/`, `.almanac/topics.yaml`, `.almanac/review.yaml`, and `.almanac/runs/` as inspectable local artifacts.
- Keep `index.db` generated and disposable.
- Keep viewer assets as a small bundled static app. The viewer is a local presentation adapter, not a separate product backend.
- Keep network access opt-in and source-specific. GitHub/source ingest can request network; local file ingest should not.
- Keep package install/update concerns under `src/platform/install/` and `src/platform/update/`, not in command files.

Anti-recommendations:

- Do not make a cloud service or hosted sync layer part of the core architecture.
- Do not make the viewer the source of truth.
- Do not introduce a browser framework build pipeline unless the vanilla viewer can no longer handle a concrete feature.

## 8. Scheduled Background Jobs: OS Scheduler As Adapter

Apple's [launchd daemon/agent guide](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html) shows jobs as plist-defined `ProgramArguments` managed by the OS. The [systemd timer manual](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html) frames Linux timers as unit files that activate matching services. This supports CodeAlmanac's current scheduler split:

- `platform/automation`: writes/reads/removes scheduler entries.
- `capture sweep`: decides transcript eligibility.
- `garden`: executes graph maintenance.
- `process`: records and serializes write-capable runs.

Recommendations:

- Keep scheduler adapters dumb. They should know labels, paths, intervals, environment, and status. They should not know transcript quiet-window policy or Garden semantics.
- Add Linux as `src/platform/automation/systemd.ts` only when Linux support is actually implemented. Use the same `ScheduledTaskDefinition` vocabulary if it holds.
- Preserve manual equivalence: anything scheduled should be runnable as the same CLI command.
- Keep the per-wiki operation queue. SQLite WAL allows concurrent readers, but wiki writes and LLM-driven page edits still need single-writer semantics.

Anti-recommendations:

- No always-on CodeAlmanac daemon.
- No provider hook path as a coequal automation product.
- No scheduler-specific capture behavior.
- No broad "automation engine" until there is a real third or fourth scheduled operation whose current explicit task catalog fails.

## 9. CLI Framework Prior Art: Commander Is Still The Right Weight

[Command Line Interface Guidelines](https://clig.dev/) is the most relevant CLI source for CodeAlmanac's UX: quiet/scriptable output, explicit JSON, no unexpected prompts in non-TTY contexts, and careful secret handling. [oclif](https://oclif.io/docs/features/) is useful prior art for large extensible CLIs with plugins, hooks, autogenerated docs, installers, and autocomplete.

CodeAlmanac should learn from oclif without adopting it. The current `commander` setup plus named registration modules is a better match for a small open-source package where architecture risk is already "too many special paths".

Recommendations:

- Keep `src/cli/register-*.ts` grouping by command family.
- Keep small single-file commands as files and multi-file commands as command folders.
- Keep `CommandResult` / `renderOutcome` as the neutral CLI result boundary.
- Improve help/examples if needed; do not switch frameworks to get documentation generation.

Anti-recommendations:

- No oclif migration.
- No plugin CLI surface until external plugin installation exists as a product requirement.
- No class-per-command hierarchy unless Commander action functions become untestable.

## 10. Local Web Viewer: A Read Adapter Over Shared Query Models

The viewer should be understood as a second driving adapter beside the CLI, not as a separate application layer. That follows ports/adapters and CQS more than frontend-framework prior art.

Current good shape:

- `src/cli/commands/serve.ts` is a thin command wrapper.
- `src/viewer/server.ts` owns HTTP routing.
- `src/viewer/api.ts` assembles viewer payloads.
- `src/wiki/query/page-view.ts` and `src/wiki/query/search.ts` hold shared query logic.
- `src/viewer/jobs.ts` delegates run storage to `src/process/index.ts`.
- `viewer/` static files are bundled and disposable.

Recommendations:

- If a viewer feature needs new data, first ask whether it is a shared read model. If yes, put it under `src/wiki/query/` or `src/process/` and call it from both CLI and viewer.
- Keep viewer job projections separate from raw run storage and raw harness event parsing.
- Keep viewer writes out of scope unless the product explicitly decides to add an editing UI.

Anti-recommendations:

- No Next.js/React layer for the current viewer.
- No viewer-private parser for markdown, wikilinks, source records, or run records.
- No hidden API server state; refresh should always reconstruct from local files/index.

## 11. Target Shape For The Audit

Recommended mental model:

```text
src/cli/commands/          primary adapter: parse/render command calls
src/viewer/                primary adapter: local HTTP + viewer payloads
src/operations/            Build / Absorb / Garden use-case construction
src/capture/               quiet-session capture use case + transcript discovery
src/ingest/                source-ref resolution and source context construction
src/process/               run lifecycle, queue, logs, snapshots, run records
src/harness/               provider-neutral runtime port + provider adapters
src/wiki/indexer/          markdown -> SQLite projection
src/wiki/query/            shared read models for CLI/viewer
src/wiki/topics/           topic DAG persistence and rewrites
src/platform/automation/   scheduler adapters and task catalog
src/platform/install/      npm/global install and launcher runtime
src/platform/update/       self-update check/install state
src/config/                persisted config schema/codec/store/origins
```

Recommended dependency posture:

```text
CLI/viewer/scheduler adapters
  -> named application behavior
    -> provider-neutral specs, read models, run lifecycle, capture policy
      -> narrow driven adapters for SQLite, filesystem, providers, OS schedulers
```

The target is not strict layering by directory. It is "no subsystem should know a lower-level external shape unless that subsystem owns the adapter for it."

## Audit Checklist From Prior Art

Use these questions during the architecture audit:

- Does this code name a product concept, or only a technical layer?
- Is this file a driving adapter, application behavior, or driven adapter?
- Does a command file decide product policy that another surface will need?
- Does an inner module import provider SDK types, launchd plist shapes, Commander objects, or viewer route details?
- Is a special case protecting a real invariant, or compensating for a missing general seam?
- Is there a second concrete implementation before adding a registry or port?
- Is SQLite being used as a generated local read model, or is it quietly becoming source of truth?
- Is a background job runnable manually through the same command path?
- Would extracting a pure decision function make the behavior easier to test without hiding necessary I/O?
- Would a new tracked file become public maintenance surface without a durable owner?

## Source List

- Alistair Cockburn, [Hexagonal Architecture, the original 2005 article](https://alistair.cockburn.us/hexagonal-architecture)
- Robert C. Martin, [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- Martin Fowler, [Service Layer](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- Martin Fowler, [Registry](https://martinfowler.com/eaaCatalog/registry.html)
- Martin Fowler, [Command Query Separation](https://martinfowler.com/bliki/CommandQuerySeparation.html)
- Martin Fowler, [CQRS](https://martinfowler.com/bliki/CQRS.html)
- Harry Percival and Bob Gregory, [Architecture Patterns with Python: Service Layer](https://www.cosmicpython.com/book/chapter_04_service_layer.html)
- Harry Percival and Bob Gregory, [Architecture Patterns with Python: Unit of Work](https://www.cosmicpython.com/book/chapter_06_uow.html)
- Functional Architecture, [Functional Core, Imperative Shell](https://functional-architecture.org/functional_core_imperative_shell/)
- Aanand Prasad et al., [Command Line Interface Guidelines](https://clig.dev/)
- SQLite, [Appropriate Uses For SQLite](https://www.sqlite.org/whentouse.html)
- SQLite, [Write-Ahead Logging](https://www.sqlite.org/wal.html)
- npm Docs, [package.json](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/)
- Apple Developer Archive, [Creating Launch Daemons and Agents](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
- systemd manual, [systemd.timer](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html)
- Ink & Switch, [Local-first software](https://www.inkandswitch.com/essay/local-first/)
- oclif, [Features](https://oclif.io/docs/features/)
