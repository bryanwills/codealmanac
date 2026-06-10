# Provider, Harness, Config, Readiness, and Connector Boundary Audit

Date: 2026-06-08

Scope: `src/agent`, `src/harness`, `src/config`, `src/connectors`, provider-adjacent command code, process/log surfaces that persist harness events, and provider-related tests.

Required context read first: `MANUAL.md`, `.almanac/README.md`, `.claude/agents/review.md`, and the Almanac pages `provider-lifecycle-boundary`, `harness-providers`, `claude-agent-sdk`, `global-agent-instructions`, and `operation-prompts`.

No source code was modified during this audit.

## Findings

### 🟠 Restructure: connector runtime requirements are stale harness machinery

`/Users/rohan/Desktop/Projects/codealmanac/src/harness/types.ts:9` defines `ConnectorRuntimeRequirement` as a Composio/GitHub-specific shape, and `/Users/rohan/Desktop/Projects/codealmanac/src/harness/types.ts:41` carries it on the provider-neutral `AgentRunSpec`. The only runtime behavior still tied to it is `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/app-server.ts:361`, where Codex enables sandbox network access when `spec.connectors` is non-empty.

Production ingest no longer needs that connector field for the network decision: `/Users/rohan/Desktop/Projects/codealmanac/src/cli/commands/operations.ts:198` explicitly sets `networkAccess: input.value.kind === "source"`. The remaining connector path is carried through `/Users/rohan/Desktop/Projects/codealmanac/src/operations/run.ts:46`, `/Users/rohan/Desktop/Projects/codealmanac/src/operations/run.ts:68`, `/Users/rohan/Desktop/Projects/codealmanac/src/operations/absorb.ts:22`, `/Users/rohan/Desktop/Projects/codealmanac/src/operations/absorb.ts:37`, and `/Users/rohan/Desktop/Projects/codealmanac/src/operations/absorb.ts:49`, but it is not populated by the current command flow.

Recommended shape: remove `connectors` and `ConnectorRuntimeRequirement` from `AgentRunSpec` unless a current production operation truly needs provider adapters to receive connector identity. Keep the implemented sandbox concern as `networkAccess` or a neutral `runtimeRequirements.network` field. If connector runtime injection becomes real later, give it a connector-owned contract instead of a Composio/GitHub shape inside the harness provider spec.

Why it matters: future provider adapters should not be taught that every Almanac run may carry Composio account ids when the current adapter only needs a boolean sandbox permission.

### 🟠 Restructure: normalized tool display events persist raw Codex protocol payloads

`/Users/rohan/Desktop/Projects/codealmanac/src/harness/events.ts:35` defines `HarnessToolDisplay` as the normalized display object for tool events, but `/Users/rohan/Desktop/Projects/codealmanac/src/harness/events.ts:45` includes `raw?: unknown`. Codex then fills that field for every display shape in `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/tool-display.ts:46`, `:54`, `:63`, `:72`, `:81`, `:89`, and `:125`. The helper at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/tool-display.ts:179` copies the whole provider item and adds `_codealmanacProviderIds`.

The process log layer strips only top-level event envelope raw data at `/Users/rohan/Desktop/Projects/codealmanac/src/process/logs.ts:76`, then persists the remaining event body at `/Users/rohan/Desktop/Projects/codealmanac/src/process/logs.ts:48`. That means nested `event.display.raw` survives into `.almanac/runs/*.jsonl` and into viewer parsing at `/Users/rohan/Desktop/Projects/codealmanac/src/viewer/jobs.ts:150`.

Recommended shape: remove `raw` from `HarnessToolDisplay` for persisted events, or make raw provider payload capture an explicit debug-only top-level field that the process log can omit by default. If thread/turn ids are needed by viewers or diagnostics, normalize them as first-class display/event fields such as `providerThreadId` and `providerTurnId`; do not hide them in `_codealmanacProviderIds` inside a raw provider item.

Why it matters: `.almanac/runs` and the viewer API become public-ish audit surface. Persisting full provider items makes Codex app-server protocol fields part of CodeAlmanac's long-term data shape by accident.

### 🟠 Restructure: readiness view parses provider prose instead of receiving structured status

Provider readiness already has structured booleans on `ProviderStatus`, but `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/view.ts:190` still inspects `status.detail` with `/not (logged|signed) in|not authenticated/i` before falling back to `status.authenticated`. The same view derives `account` by treating any non-generic detail string as identity at `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/view.ts:98` and `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/view.ts:212`.

The providers currently overload `detail` with different meanings: Claude puts email, `ANTHROPIC_API_KEY set`, `logged in`, `not logged in`, or an install message in `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/providers/claude/index.ts:83`; Codex forwards the first status-output line as `detail` in `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/providers/codex-cli.ts:155`; Cursor does the same in `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/providers/cursor-cli.ts:39`.

`fixCommand` is also provider-specific data held in central maps at `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/view.ts:52` and `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/view.ts:58`, then selected by `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/view.ts:199`.

Recommended shape: make provider readiness return a normalized status object with fields such as `readiness`, `accountLabel`, `installFix`, and `loginFix`, while keeping `detail` as human prose only. The readiness view should compose display rows from structured provider facts, not parse provider status text or own provider-specific fix commands.

Why it matters: status prose is currently a hidden data contract. Changing one provider's wording can change setup, `almanac agents`, or doctor behavior.

### 🟡 Fix: doctor has a parallel injected provider-status path

`/Users/rohan/Desktop/Projects/codealmanac/src/cli/commands/doctor/agents.ts:9` builds the normal provider setup view, but when `options.spawnCli` is present it supplies statuses from `injectedProviderStatuses()` instead of letting the readiness providers run. That helper calls only Claude auth at `/Users/rohan/Desktop/Projects/codealmanac/src/cli/commands/doctor/agents.ts:40`, then hard-codes Codex and Cursor as missing at `/Users/rohan/Desktop/Projects/codealmanac/src/cli/commands/doctor/agents.ts:54` and `/Users/rohan/Desktop/Projects/codealmanac/src/cli/commands/doctor/agents.ts:60`.

This bypasses the readiness providers that already accept an injected `spawnCli`: Codex at `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/providers/codex-cli.ts:148`, Cursor at `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/providers/cursor-cli.ts:36`, and provider iteration at `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/providers/status.ts:15`.

Recommended shape: delete `injectedProviderStatuses()` and pass `spawnCli` through the existing readiness catalog, or call `listProviderStatuses(options.spawnCli)` from the doctor path.

Why it matters: doctor currently has its own provider model for tests and injected runs, so it can report a provider missing even when the readiness provider would report it ready.

### 🟡 Fix: provider identity and defaults are duplicated across catalogs and command helpers

There are legitimate separate lifecycles here: config needs allowed ids, harness needs runtime capabilities, and readiness needs executable/status/model-choice behavior. The drift risk is that basic identity and defaults are repeated rather than shared.

Examples:

- `/Users/rohan/Desktop/Projects/codealmanac/src/config/providers.ts:1` owns `ALL_AGENT_PROVIDER_IDS`.
- `/Users/rohan/Desktop/Projects/codealmanac/src/harness/types.ts:5` separately defines `HarnessProviderId`.
- `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/metadata.ts:31` owns harness display names and default models.
- `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/providers/claude/index.ts:16` defines the Claude default model again, and `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/providers/claude/index.ts:18` repeats Claude display/default/executable metadata.
- `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/providers/codex-cli.ts:14` and `/Users/rohan/Desktop/Projects/codealmanac/src/agent/readiness/providers/cursor-cli.ts:13` repeat the same provider identity fields for Codex and Cursor.
- `/Users/rohan/Desktop/Projects/codealmanac/src/cli/commands/setup/agent-choice.ts:280` hard-codes Claude model labels already present in readiness model choices, and `/Users/rohan/Desktop/Projects/codealmanac/src/cli/commands/setup/agent-choice.ts:287` hard-codes provider display names.
- `/Users/rohan/Desktop/Projects/codealmanac/src/cli/commands/operations.ts:301`, `/Users/rohan/Desktop/Projects/codealmanac/src/process/spec.ts:66`, and `/Users/rohan/Desktop/Projects/codealmanac/src/process/records.ts:202` repeat provider-id validation with string literals.

Recommended shape: do not merge readiness into harness. Instead, make one small shared provider identity catalog for id/display/default model, or derive readiness display/default from `HARNESS_PROVIDER_METADATA` while readiness adds executable and status behavior. Export a single provider-id guard for operation/process validation.

Why it matters: a future default-model upgrade can update setup but not runtime, or runtime but not setup, and both failures will look like provider bugs rather than catalog drift.

### 🟡 Fix: Codex legacy exec compatibility is still exported but no production path uses it

`/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex.ts:40` declares `CodexHarnessProviderDeps.runCli`, but `createCodexHarnessProvider()` never reads it. The same facade exports `buildCodexExecRequest`, `runCodexCli`, and JSONL event handling at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex.ts:13`, `:16`, `:20`, and `:22`. A repo search found those exec/JSONL exports used by tests and internal legacy modules, not by production operation execution.

The actual provider run path uses app-server only: `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex.ts:56` selects `runCodexAppServer`, and `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex.ts:100` calls `runAppServer(spec, hooks)`.

Recommended shape: delete the unused `runCli` dependency now. Then decide whether `codex exec --json` is still a supported compatibility transport. If it is not, remove the exec request/runner/tests. If it is, move it behind an explicitly named legacy module and make the selection rule visible in production code.

Why it matters: dead compatibility surfaces keep the old transport alive in maintainer heads, and tests can make an unsupported path look intentionally supported.

### 🟡 Fix: Codex failure classification still relies on provider prose and JSON substring extraction

`/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/failures.ts:4` accepts a raw string and classifies model/auth/process failures by substring and regex. It extracts JSON by slicing between the first `{` and last `}` at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/failures.ts:71`, and extracts status codes with a prose regex at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/failures.ts:87`.

Some upstream paths have structured error objects before this point. JSON-RPC responses carry `error.code` and `error.data` in `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/app-server.ts:21`, but `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/app-server.ts:182` reduces that to `new Error(message)`. Error notifications also read nested fields at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/app-notifications.ts:181` and pass only the chosen message to `classifyCodexFailure()`.

Recommended shape: normalize provider error objects at the app-server edge and pass a structured value into classification, for example `{ message, code, data, statusCode }`. Keep regex/string extraction only as a documented fallback for legacy `codex exec` stderr.

Why it matters: provider wording is not a stable protocol. Classification for auth and model availability should prefer structured data whenever the transport provides it.

### 🔵 Polish: project instruction docs are stale around provider boundaries

`/Users/rohan/Desktop/Projects/codealmanac/CLAUDE.md:42` still describes `src/agent/` as an "Agent facade, provider registry, provider adapters" directory with `sdk.ts` and `providers/`, but current source has `auth`, `instructions`, `readiness`, `prompts`, and `types`. `/Users/rohan/Desktop/Projects/codealmanac/CLAUDE.md:87` also says each provider exposes metadata, readiness, and run behavior, while the current architecture deliberately splits runtime harness adapters from readiness providers.

The required wiki page `.almanac/pages/claude-agent-sdk.md` also disagrees with current code. It says the Claude adapter does not pass `outputFormat` or preserve structured output at `/Users/rohan/Desktop/Projects/codealmanac/.almanac/pages/claude-agent-sdk.md:43`, and says `structuredOutput: false` at `/Users/rohan/Desktop/Projects/codealmanac/.almanac/pages/claude-agent-sdk.md:69`. Current code passes `outputFormat` at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/claude.ts:285`, builds it at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/claude.ts:300`, preserves `structured_output` at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/claude.ts:147`, and marks Claude structured output true at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/metadata.ts:47`.

Recommended shape: update docs/wiki after source cleanup or as a small documentation pass. Do not let stale docs drive source shape; the code is truth here.

Why it matters: the provider boundary is already subtle, and stale instructions can cause future agents to recreate deleted `src/agent/providers` or old SDK facades.

## Clean Boundaries Worth Preserving

The runtime/readiness split is directionally correct. `src/harness/providers/` owns execution adapters and runtime capability metadata, while `src/agent/readiness/` owns setup/status/model-choice views. Do not collapse those into one provider mega-layer.

Claude auth is in the right neighborhood. `/Users/rohan/Desktop/Projects/codealmanac/src/agent/auth/claude.ts:36` resolves the executable for both runtime and readiness, and `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/claude.ts:24` imports that shared auth/executable layer instead of duplicating it.

Codex instruction installation is correctly outside readiness and harness. `/Users/rohan/Desktop/Projects/codealmanac/src/agent/instructions/codex.ts:11` owns AGENTS-file writing, and `/Users/rohan/Desktop/Projects/codealmanac/src/agent/install-targets.ts:47` orchestrates Claude/Codex instruction installation without pretending that instruction files are runtime provider state.

The final-output contract is a good provider-neutral shape. `/Users/rohan/Desktop/Projects/codealmanac/src/harness/final-output.ts:7` carries schema output as a harness-level contract, Claude maps it to `outputFormat`, and Codex app-server passes `outputSchema` at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/app-server.ts:347`. This is the right replacement for scraping final prose.

Provider session persistence is correctly expressed at the spec level. `/Users/rohan/Desktop/Projects/codealmanac/src/operations/run.ts:73` sets `providerSession.persistence = "ephemeral"` for operation runs, Claude maps it at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/claude.ts:291`, and Codex maps it at `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/app-server.ts:312`.

The Codex app-server adapter is split into sensible responsibility modules. Request construction, app-server process/RPC handling, notification mapping, actor tracing, usage parsing, tool-display shaping, and failure classification are separate files under `/Users/rohan/Desktop/Projects/codealmanac/src/harness/providers/codex/`. That split should stay; the issues above are about stale fields/raw leakage, not about recombining the adapter.

Process logs now use normalized actor fields instead of provider-private actor payloads. `/Users/rohan/Desktop/Projects/codealmanac/src/process/logs.ts:47` persists `event.actor ?? inferActor(event)`, and `/Users/rohan/Desktop/Projects/codealmanac/test/process-logs.test.ts:46` explicitly protects against inferring actors from provider-private display raw. Preserve that direction while removing nested display raw leakage.

Config is mostly organized by reason-to-change. `src/config/schema.ts`, `codec.ts`, `store.ts`, `origins.ts`, `paths.ts`, and `providers.ts` are distinct and understandable. The main config problem in this audit is provider identity duplication and connector-runtime carry-through, not the config module split itself.

Connector account storage correctly avoids persisted secrets. `/Users/rohan/Desktop/Projects/codealmanac/src/config/schema.ts:19` stores the Composio API key environment variable name, not the key value, and `/Users/rohan/Desktop/Projects/codealmanac/src/connectors/composio/accounts.ts:132` resolves the actual secret from the environment at use time.

Capture transcript discovery is separate from runtime harness providers. `/Users/rohan/Desktop/Projects/codealmanac/src/capture/discovery/claude.ts:12` and `/Users/rohan/Desktop/Projects/codealmanac/src/capture/discovery/codex.ts:13` scan provider app transcript stores as source material, not as harness history. That matches the wiki's provider lifecycle boundary.

## Suggested Cleanup Order

1. Remove stale connector runtime fields from `AgentRunSpec`, keeping `networkAccess` as the current sandbox requirement.
2. Remove or quarantine `HarnessToolDisplay.raw`; add structured thread/turn fields only if a downstream consumer actually needs them.
3. Normalize provider readiness output so `ProviderStatus.detail` is no longer parsed for readiness/account/fixes.
4. Delete the doctor injected-status branch and use the readiness provider catalog for injected status checks.
5. Consolidate provider identity/default-model facts without merging readiness into harness.
6. Remove the unused Codex `runCli` dependency and decide whether the exec transport is real compatibility or dead test-only code.
7. Change Codex failure classification to prefer structured JSON-RPC error data.
8. Update `CLAUDE.md` and stale wiki pages after source boundaries settle.
