# Lifecycle Command Ownership And Flow Boundaries Audit

Date: 2026-06-08

Scope: lifecycle command ownership and flow boundaries in `src/cli`, `src/operations`, `src/process`, `src/capture`, `src/platform/automation`, and `src/ingest`.

Read first: `MANUAL.md`, `.almanac/README.md`, and the wiki pages `lifecycle-architecture`, `wiki-lifecycle-operations`, `lifecycle-cli`, `process-manager-runs`, `capture-flow`, `capture-automation`, `automation`, `ingest-operation`, and `build-operation`.

No source code was modified.

## Overall Take

The big lifecycle shape is mostly right: public commands route to operation specs, operation specs route to the process manager, and the process manager owns records, logs, snapshots, queueing, and reindexing. That shape should be preserved.

The weak points are at the edges: `capture sweep` still recovers durable state by parsing rendered command output, manual capture and scheduled sweep have split transcript-discovery routing, GitHub source ingest and Composio source access are two parallel mechanisms, and sqlite-free recovery keeps a second hand-written parser for command surfaces that already exist in Commander. Those are exactly the accidental-special-case risks the manual warns about.

## Findings

### 1. `capture sweep` parses CLI output to recover the run id

Severity: high.

`src/cli/commands/capture-sweep.ts:53-71` starts captures by calling `runCaptureCommand()` with `json: true`, then `src/cli/commands/capture-sweep.ts:68` calls `extractRunId(result.stdout)`. `src/cli/commands/capture-sweep.ts:110-118` then parses JSON or falls back to a regex over `capture started: run_...`.

That makes a durable lifecycle field flow through rendered CLI output. The sweep ledger needs the run id to reserve a transcript cursor; it should not depend on stdout shape. This is a text-scraping product boundary.

Recommended shape: expose a typed capture-start API below the CLI renderer. For example, a capture application service can resolve transcripts, create the Absorb spec, enqueue the run, and return `{ runId, record }`; `runCaptureCommand()` can render that typed result, and `capture sweep` can consume it directly.

Why it matters: changing human or JSON output should not be able to break scheduled capture dedupe.

### 2. Manual capture and scheduled capture have diverged discovery models

Severity: high.

Manual capture discovery is still Claude-only. `src/capture/input.ts:48-61` defaults to Claude, rejects `--all-apps`, and rejects any `--app` other than Claude unless explicit files are passed. Scheduled capture discovery supports both Claude and Codex through `src/capture/discovery/index.ts:12-17`, with provider scanners in `src/capture/discovery/claude.ts` and `src/capture/discovery/codex.ts`.

The public command surface advertises the broader intent: `src/cli/register-wiki-lifecycle-commands.ts:73-79` includes `--app`, `--all-apps`, and provider-ish capture options, while `src/cli/register-wiki-lifecycle-commands.ts:258-287` wires `capture sweep --apps`.

Recommended shape: one normalized session-discovery boundary should serve both manual capture and scheduled sweep. Manual capture may still choose "latest matching candidate" while sweep chooses "all quiet eligible candidates", but both should consume the same `SessionCandidate` source model and app scanners.

Why it matters: users should not have to learn that `capture --app codex` is unsupported while `capture sweep --apps codex` works.

### 3. GitHub source ingest and Composio source access are competing mechanisms

Severity: high.

Lifecycle ingest currently guides the agent to use local `gh`. `src/ingest/context.ts:29-44` renders GitHub PR guidance with `gh pr view` and `gh pr diff`; `src/ingest/context.ts:55-68` does the same for issues. `src/ingest/github.ts:26-43` resolves only GitHub source identity and local repo remote.

Separately, `almanac source github ...` uses Composio. `src/cli/register-setup-commands.ts:119-183` wires `connect github` and `source github issue|pr`; `src/connectors/github/source.ts:22-37` reads GitHub objects through a Composio toolkit session. The harness has a connector runtime field in `src/harness/types.ts:9-15`, and `src/operations/run.ts:46-69` can carry connectors into `AgentRunSpec`, but `src/cli/commands/operations.ts:191-202` sets only `networkAccess` and output schema for source ingest, not connector requirements.

There is also a misplaced or stale flag: `src/cli/register-wiki-lifecycle-commands.ts:82` puts `--account <alias>` on `capture`, not `ingest`, and the capture action does not pass it anywhere.

The wiki is stale against source here. `.almanac/pages/ingest-operation.md:80-88` says current GitHub ingest uses Composio, does not depend on `gh`, and routes source inspection through `almanac source github ...`. The tests currently assert the opposite in `test/operation-commands.test.ts:363-367` and `test/ingest-input.test.ts:140-145`.

Recommended shape: choose one product truth for local GitHub ingest.

- If local `gh` is the intended OSS path, remove or park connector-backed ingest claims, remove the orphan `capture --account` flag, and keep Composio as a separate `source`/hosted-connector experiment.
- If Composio is the intended path, make `resolveIngestInput()` produce a source brief with connector runtime requirements, pass `connectors` into `runAbsorbOperation()`, and render `almanac source github ...` or provider-native connector guidance instead of `gh`.

Why it matters: this is not just documentation drift; it is a split source-access architecture with two auth stories, two command surfaces, and unclear lifecycle ownership.

### 4. `src/cli/commands/operations.ts` is still doing domain-specific operation work

Severity: medium.

The file is 462 lines and owns provider selection, capture transcript resolution, ingest input resolution, operation dispatch, result rendering, error rendering, command-context construction, and GitHub PR sticky-comment output selection. The most questionable operation-specific logic is `src/cli/commands/operations.ts:212-232`, where a command adapter detects a single GitHub PR and attaches `ALMANAC_OPERATION_REPORT_OUTPUT`. `src/cli/commands/operations.ts:381-407` also classifies errors by message substring (`"no .almanac/"`) and a GitHub-specific error type.

Some orchestration in this file is expected, but this one has become the place lifecycle edge cases accumulate.

Recommended shape: keep command files as command adapters. Move source-specific output contracts and operation context policy into the ingest/operation boundary, and replace message-substring error classification with typed lifecycle errors.

Why it matters: source kinds and output contracts will grow; if they grow in the command adapter, command files become the de facto operation layer.

### 5. The sqlite-free path is valuable but now duplicates too much command routing

Severity: medium.

`src/cli.ts:84-93` routes setup shortcuts and sqlite-free commands before Commander loads. The reason is legitimate: recovery commands must work when `better-sqlite3` cannot load. But `src/cli/sqlite-free.ts:32-41` now mirrors setup, automation, agents, config, set, update, doctor, and uninstall. `src/cli/sqlite-free.ts:109-153` hand-routes automation; `src/cli/sqlite-free.ts:324-359` reparses automation install flags; `src/cli/sqlite-free.ts:371-449` reparses setup flags.

The lifecycle wiki already records that this path has drifted before. The code now carries a permanent "remember to update two parsers" obligation for setup and automation.

Recommended shape: preserve sqlite-free recovery, but shrink or formalize it. Either restrict it to the minimum recovery surface (`setup`, `doctor`, `automation status|uninstall|install`) or define a small shared option spec that both Commander and sqlite-free parsing consume.

Why it matters: recovery routing is justified; parser drift is not.

### 6. Scheduled Garden by default has weaker evidence than scheduled capture

Severity: medium.

Default automation installs both capture and Garden. `src/platform/automation/tasks.ts:77` sets `DEFAULT_AUTOMATION_TASK_IDS` to `["capture", "garden"]`, and setup calls `runAutomationInstall({ tasks: ["capture", "garden"], ... })` in `src/cli/commands/setup/automation-step.ts:62-68`.

Capture automation has a strong product invariant: quiet-session evidence becomes eligible after a quiet window. Scheduled Garden is looser: it wakes every `4h` by default (`src/platform/automation/tasks.ts:12`, `src/platform/automation/tasks.ts:47-57`) and asks an agent to reshape the whole wiki graph. That may be useful, but it is broader, more expensive, and more surprising than capture.

Recommended shape: keep `almanac garden` and maybe keep `automation install garden`, but reconsider enabling scheduled Garden by default during setup. Make the default either capture-only or explicitly justified by a product policy such as "Garden only after accumulated page changes or health issues."

Why it matters: recurring whole-graph LLM maintenance has higher trust and cost risk than scheduled transcript capture.

### 7. Setup-specific automation command overrides bypass the task-definition source of truth

Severity: low to medium.

The good source of truth is `src/platform/automation/tasks.ts:29-69`, where capture, Garden, and update task definitions own labels, defaults, log names, working-directory policy, and default command arguments. But setup overrides program arguments directly through `src/cli/commands/setup/automation-step.ts:69-74`, `src/cli/commands/setup/automation-step.ts:99-105`, and hardcoded helpers in `src/cli/commands/setup/automation-step.ts:128-138`.

The npx/durable-install distinction is real, but the current shape pushes scheduler command construction back into setup.

Recommended shape: let task definitions accept a launcher mode (`absolute-node-entrypoint` vs `env-almanac`) or let the scheduler adapter construct program arguments from a typed launcher. Setup should choose the launcher, not rebuild task commands.

Why it matters: task definitions should stay the scheduler identity source of truth.

### 8. Capture provenance classification is narrow and coupled to run records

Severity: low to medium.

`src/capture/sweep.ts:103-105` skips internal Almanac sessions by calling `isInternalAlmanacSession()`, which reads prior process-manager records and compares `candidate.sessionId` against `RunRecord.providerSessionId` in `src/capture/sweep.ts:180-193`.

That is a useful guard, but it is not the broader provenance boundary described in the wiki. It does not classify candidates into ordinary project work, helper/subagent, or maintenance exhaust as a first-class source category. It also couples sweep eligibility to process-manager provider-session persistence.

Recommended shape: keep the run-record check as one signal, but introduce a small candidate provenance classifier before cursor evaluation. It should own app-specific maintenance markers, subagent/helper exclusion, provider-session-id checks, and explicit skip reasons.

Why it matters: the 2026-05-28 cost incident was a provenance failure before it was an Absorb judgment failure.

### 9. Manual Claude transcript fallback reads whole files to inspect the head

Severity: low.

`src/capture/input.ts:199-220` falls back from directory-name matching to checking transcript content for `"cwd":"<repoRoot>"`. The helper named `readHead()` in `src/capture/input.ts:223-225` calls `readFile()` and then slices, so it loads the whole transcript to read the first 4 KB.

The wiki already calls this out as a known performance problem. The scheduled discovery path has the better shape: `src/capture/discovery/jsonl.ts:15-24` uses `fs.open().read()` with a bounded 64 KB buffer.

Recommended shape: use the scheduled discovery helper or the same bounded-read pattern for manual capture fallback.

Why it matters: large transcript stores should not turn command startup into hundreds of MB of avoidable I/O.

### 10. Deprecated lifecycle aliases are still public code paths

Severity: low.

`src/cli/register-wiki-lifecycle-commands.ts:291-320` keeps `almanac capture status` and `almanac ps` as warnings that route to jobs. This is low cost, but it is still public compatibility surface.

Recommended shape: keep them only if there is a concrete compatibility window. Otherwise delete the aliases and their tests/docs once users have had a release cycle.

Why it matters: dead compatibility paths become architecture when nobody remembers why they remain.

### 11. Repo docs still mention `bootstrap` as a current lifecycle exception

Severity: low.

`CLAUDE.md` still says "The CLI never reads or writes page content. Only `capture` and `bootstrap` touch AI or write pages." Current lifecycle pages and code say V1 deleted public `bootstrap`; Build is behind `almanac init`.

Recommended shape: update repo instructions to say `init`, `capture`, `ingest`, and `garden` are the write-capable lifecycle commands, while query/edit commands stay deterministic.

Why it matters: stale top-level instructions are especially costly in a repo whose primary consumer is an AI coding agent.

## Boundaries Worth Preserving

### Operation specs are the right semantic boundary

`src/operations/run.ts:38-82` centralizes prompt assembly, base tools, provider session persistence, output schema, metadata, and target information into `AgentRunSpec`. `src/operations/build.ts:27-40`, `src/operations/absorb.ts:31-52`, and `src/operations/garden.ts:22-35` then create operation-specific specs without knowing provider runtime details.

Keep this. Future lifecycle work should add to this spec boundary rather than bypass it from command files.

### Process manager ownership is mostly clean

`src/process/background.ts:47-104` writes the spec, queued record, and log before waking `__run-worker`. `src/process/background.ts:118-154` drains queued runs under the worker lock. `src/process/manager.ts:50-123` enforces the foreground single-writer lock, and `src/process/manager.ts:195-323` owns execution, event logging, page snapshots, page-change summaries, terminal records, and reindex-on-success.

Keep this. It is the clearest ownership boundary in the lifecycle architecture.

### Run records as the durable audit source are correct

`src/process/records.ts:50-58` writes run records atomically, `src/process/spec.ts:16-26` persists the exact run spec, and `src/process/logs.ts:33-56` writes normalized event logs. That matches the wiki's claim that `.almanac/runs/` is the canonical job transcript and audit record.

Keep this. Do not move run observability into provider transcripts.

### Automation task definitions are the right scheduler model

`src/platform/automation/tasks.ts:29-69` defines capture, Garden, and update as typed scheduled tasks. `src/platform/automation/launchd.ts:74-130` owns plist rendering, bootstrapping, removal, and status. `src/platform/automation/legacy-hooks.ts:6-18` isolates historical hook cleanup.

Keep this split. New scheduled work should add task definitions, not more branches in `src/cli/commands/automation.ts`.

### Capture sweep has a good domain core once start routing is fixed

`src/capture/sweep.ts:74-178` is a real coordinator over candidates, ledger reconciliation, locks, cursor decisions, enqueueing, and summaries. `src/capture/ledger.ts:76-102` owns pending-run reconciliation, and `src/capture/ledger.ts:163-188` owns the activation-baseline cursor calculation.

Keep this domain core. Fix the `startCapture` implementation so it receives typed run-start data instead of parsing command output.

### Ingest source-ref parsing is a useful seam

`src/ingest/source-ref.ts:30-65` parses shorthand source refs, `src/ingest/source-ref.ts:67-113` parses GitHub and generic web URLs, and `src/ingest/input.ts:21-75` separates local paths from source refs before command dispatch. That is the right seam for future source kinds.

Keep the seam, but decide whether the source runtime is local `gh`, Composio, or another connector path before adding more source kinds.

## Single Most Important Improvement

Create a lifecycle application layer below Commander and above operations:

```ts
capture.start(options) -> { runId, record, resolvedTranscripts }
capture.sweep(options) -> { summary }
ingest.start(options) -> { runId, record, resolvedInput }
automation.install(options) -> { installedTasks }
```

Command files should render those typed results. Sweep, setup, and other internal callers should consume those typed results. That one change would remove stdout parsing, reduce command-file domain logic, and make sqlite-free recovery easier to constrain.
