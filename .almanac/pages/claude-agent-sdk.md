---
title: Claude Agent SDK
summary: >-
  `@anthropic-ai/claude-agent-sdk` is isolated behind the Claude harness adapter, which maps Almanac
  run specs to Claude tools, auth checks, events, and limits.
topics:
  - stack
  - agents
  - provider-harness
sources:
  - id: structured-output-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-07 structured-output audit that led to the Claude adapter mapping for SDK
      outputFormat and structured_output.
  - id: claude
    type: file
    path: src/harness/providers/claude.ts
    note: Migrated from legacy files.
  - id: types
    type: file
    path: src/harness/types.ts
    note: Migrated from legacy files.
  - id: events
    type: file
    path: src/harness/events.ts
    note: Migrated from legacy files.
  - id: claude-2
    type: file
    path: src/agent/auth/claude.ts
    note: Migrated from legacy files.
  - id: index
    type: file
    path: src/agent/readiness/providers/claude/index.ts
    note: Migrated from legacy files.
  - id: prompts
    type: file
    path: src/agent/prompts.ts
    note: Migrated from legacy files.
  - id: claude-harness-provider-test
    type: file
    path: test/claude-harness-provider.test.ts
    note: Migrated from legacy files.
  - id: setup-test
    type: file
    path: test/setup.test.ts
    note: Migrated from legacy files.
  - id: sdk-integration-session
    type: conversation
    path: /Users/rohan/.codex/sessions/2026/05/28/rollout-2026-05-28T18-27-05-019e70e9-b7d7-7900-9fc0-da2a6f0b532d.jsonl
    note: Records the 2026-05-28 session covering Claude Agent SDK integration, the harness adapter boundary, and the structured-output mapping for the Claude provider.
  - id: sdk-types
    type: manual
    note: >-
      Inspected node_modules/@anthropic-ai/claude-agent-sdk/sdk.d.ts locally to read the SDK's
      TypeScript surface (outputFormat, structured_output, tool shapes). This file is an installed
      dependency, not tracked in the repository.
verified: 2026-06-07T00:00:00.000Z

---

# Claude Agent SDK

`@anthropic-ai/claude-agent-sdk` is now used through the V1 Claude harness adapter, not through the deleted bootstrap/capture SDK wrapper. The repo keeps Claude-specific SDK types inside `src/harness/providers/claude.ts`; operation code only sees [[harness-providers]] types such as `OperationSpec`, `HarnessEvent`, and `HarnessResult`.

## Where we use it

- `src/harness/providers/claude.ts` — imports `query()` and maps `OperationSpec` to Claude SDK options.
- `src/agent/auth/claude.ts` — checks installed/authenticated Claude CLI state and resolves the Claude executable for both readiness views and the runtime harness.
- `src/agent/prompts.ts` — loads V1 operation prompts from the bundled `prompts/` directory.

## Adapter mapping

The adapter maps base tool requests to Claude tool names: read to `Read`, write to `Write`, edit to `Edit`, search to `Glob` and `Grep`, shell to `Bash`, and web to `WebSearch` and `WebFetch`. It passes the mapped list to both `tools` and `allowedTools`, sets `permissionMode: "dontAsk"`, sets `includePartialMessages: true`, and sets SDK `persistSession: false` when `OperationSpec.providerSession.persistence` is `ephemeral`.

When `OperationSpec.agents` is present, the adapter maps each helper `OperationAgentSpec` to a Claude `AgentDefinition` and ensures the main tool list includes `Agent`. V1 operations do not hardcode a reviewer agent; helper agents are generic harness data.

## Event normalization

Claude `SDKMessage` events are translated to `HarnessEvent` records. Text deltas, assistant text, tool uses, tool results, errors, and final result messages all flow through the same event hook used by [[process-manager-runs]]. Cost, turns, usage, and provider session id are preserved when the SDK exposes them.

The installed SDK type definitions expose `Options.outputFormat` and a result-message `structured_output` field. `buildClaudeOptions()` maps `OperationSpec.output.kind === "json_schema"` to SDK `outputFormat`, and the result handler preserves SDK `structured_output` as `HarnessResult.output`. When the SDK does not return structured output, the adapter falls back to parsing the final result text against the same `FinalOutputSpec`. That makes Claude structured output a current [[harness-providers|harness capability]], with `test/claude-harness-provider.test.ts` covering the option mapping and result preservation path. [@structured-output-session]

## Model and limits

Default model is `claude-sonnet-4-6` (from `HARNESS_PROVIDER_METADATA.claude.defaultModel`). Per-job model override passes through `OperationSpec.provider.model`. Effort values `low`, `medium`, `high`, and `max` map directly to Claude SDK's `effort` option; any other value is dropped.

`maxTurns` defaults to `100` in `buildClaudeOptions`; operations currently override this to `150` via `OperationSpec.limits.maxTurns`. `maxBudgetUsd` maps to `limits.maxCostUsd` when present.

## Session persistence and tags

The SDK options include `persistSession`, and the installed type definitions expose `tagSession(sessionId, tag | null)` plus a `tag` field on session info. This matters for [[capture-automation]] because Claude has two usable provider-side provenance controls: routine Almanac maintenance can run with `persistSession: false`, and exceptional persisted sessions can be marked with an `almanac` tag after the provider session id is known.

Provider session history is not CodeAlmanac's audit system. The jobs layer writes `.almanac/jobs/` records, JSONL harness events, specs, page changes, and job logs for [[process-manager-runs]]. Claude transcript persistence and Claude session tags are provider-side provenance controls that keep scheduled capture from treating CodeAlmanac maintenance sessions as future project evidence.

The 2026-05-28 decision prefers non-persistence over provider tagging for normal maintenance jobs. Tags remain useful for provider-side debugging or compatibility cases where a Claude transcript must exist, but `.almanac/jobs/` stays the canonical transcript surfaced by `almanac jobs` and `almanac serve`.

## Auth

Two paths: Claude subscription OAuth via the Claude CLI, or `ANTHROPIC_API_KEY`. Auth probe runs `claude auth status --json` with a 10-second timeout. On SDK 0.2.129+ the legacy `cli.js` probe is attempted as a fallback when the primary `claude` binary probe returns `loggedIn: false`. Any spawn error, timeout, non-JSON stdout, or non-zero exit with empty stdout returns `{ loggedIn: false }` rather than propagating an error. `ANTHROPIC_API_KEY` is accepted as the second gate — `assertClaudeAuth()` returns a synthetic `{ loggedIn: true, authMethod: "apiKey" }` when the key is set.

`resolveClaudeExecutable()` uses `command -v claude` to find the installed binary. The resolved path is passed as `pathToClaudeCodeExecutable` so the SDK and the auth probe agree on which binary to use. Headless auto-capture now runs through scheduler-backed [[capture-automation]] rather than app lifecycle hooks.

Provider setup tests can inject a fake `spawnCli` status probe instead of depending on a real `claude` binary on PATH. When `src/agent/readiness/providers/claude/index.ts` builds setup status with an injected probe, it treats Claude as installed and derives authentication from the injected status output or `ANTHROPIC_API_KEY`; production runtime discovery still uses `resolveClaudeExecutable()` from `[[src/agent/auth/claude.ts]]`. Keep this aligned with the Codex and Cursor readiness-provider behavior so CI can exercise model override setup paths without installing every provider CLI.

## Capabilities

From `HARNESS_PROVIDER_METADATA.claude`: `sessionPersistence: true`, `threadResume: true`, `interrupt: true`, `mcp: true`, `skills: true`, `usage: true`, `cost: true`, and `structuredOutput: true`. `reasoningEffort: false`. Subagents are supported with `programmaticPerRun: true` and `enforcedToolScopes: true`. [@structured-output-session]

## Failure classification

`classifyClaudeFailure()` in `src/harness/providers/claude.ts` maps raw error strings to typed `HarnessFailure` codes:

- `claude.not_authenticated` — error contains "Not logged in" or "authentication"
- `claude.max_budget_exceeded` — subtype is `error_max_budget_usd`
- `claude.process_failed` (or `claude.<subtype>`) — all other cases

## Old wrapper removal

`src/agent/sdk.ts`, `src/cli/commands/bootstrap.ts`, `src/cli/commands/capture.ts`, and the `.bootstrap-*.log` / `.capture-*.log` flows were removed during the V1 cleanup. Do not reintroduce a command-specific Claude runner; add mapping behavior inside the provider adapter.
