---
title: Harness Providers
summary: >-
  Harness providers are the adapter boundary that turns provider-neutral Almanac run specs into
  Claude, Codex, and future runtime executions.
topics:
  - agents
  - stack
  - systems
  - provider-harness
sources:
  - id: hosted-proposal-structured-output-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the hosted proposal discussion that checked Codex and Claude structured-output support
      and verified targeted harness tests.
  - id: types
    type: file
    path: src/harness/types.ts
    note: Migrated from legacy files.
  - id: events
    type: file
    path: src/harness/events.ts
    note: Migrated from legacy files.
  - id: tools
    type: file
    path: src/harness/tools.ts
    note: Migrated from legacy files.
  - id: index
    type: file
    path: src/harness/providers/index.ts
    note: Migrated from legacy files.
  - id: metadata
    type: file
    path: src/harness/providers/metadata.ts
    note: Defines HarnessEvent types and normalizes stream output into text, tool-use, tool-result, tool-summary, context-usage, error, and done event shapes.
  - id: claude
    type: file
    path: src/harness/providers/claude.ts
    note: Claude provider adapter; maps base tools to Claude Agent SDK tools, handles structured output, and reports cost and usage.
  - id: codex
    type: file
    path: src/harness/providers/codex.ts
    note: Codex provider facade; delegates to codex/ submodules for request construction, app-server protocol, and result projection.
  - id: app-server
    type: file
    path: src/harness/providers/codex/app-server.ts
    note: Codex app-server JSON-RPC handshake, notification streaming, turn-completion, and managed-child lifecycle for per-job runs.
  - id: app-notifications
    type: file
    path: src/harness/providers/codex/app-notifications.ts
    note: Maps Codex app-server notification types to normalized HarnessEvents.
  - id: actors
    type: file
    path: src/harness/providers/codex/actors.ts
    note: Actor and subagent trace state for Codex provider runs.
  - id: events-2
    type: file
    path: src/harness/providers/codex/events.ts
    note: Public compatibility facade re-exporting the stable import surface from Codex submodules.
  - id: failures
    type: file
    path: src/harness/providers/codex/failures.ts
    note: Classifies Codex failure types from app-server error notifications.
  - id: fields
    type: file
    path: src/harness/providers/codex/fields.ts
    note: Loose protocol-field decoding for Codex app-server message shapes.
  - id: request
    type: file
    path: src/harness/providers/codex/request.ts
    note: Constructs the three-phase Codex app-server JSON-RPC request from an OperationSpec.
  - id: result
    type: file
    path: src/harness/providers/codex/result.ts
    note: Projects app-server turn completion into a normalized HarnessResult.
  - id: status
    type: file
    path: src/harness/providers/codex/status.ts
    note: Readiness probing for the Codex app-server provider.
  - id: tool-display
    type: file
    path: src/harness/providers/codex/tool-display.ts
    note: Shapes Codex tool events into structured display details (kind, title, path, command, status, exit code, duration).
  - id: types-2
    type: file
    path: src/harness/providers/codex/types.ts
    note: Internal type definitions for the Codex app-server provider protocol.
  - id: usage
    type: file
    path: src/harness/providers/codex/usage.ts
    note: Parses tokenUsage fields from Codex app-server token-count notifications.
  - id: final-output
    type: file
    path: src/harness/final-output.ts
    note: Defines the provider-neutral FinalOutputSpec and FinalOutputResult used by the structured output contract.
  - id: reports
    type: file
    path: src/operations/reports.ts
    note: Implements the almanac_operation_report_v1 output schema whose summary field becomes the GitHub PR comment after almanac ingest.
  - id: cursor
    type: file
    path: src/harness/providers/cursor.ts
    note: Cursor provider placeholder; present in metadata as the future extension point but currently fails clearly on run.
  - id: view
    type: file
    path: src/agent/readiness/view.ts
    note: Builds the readiness projection for setup, almanac agents, and doctor from config plus provider status metadata; not the execution adapter.
  - id: providers
    type: file
    path: src/agent/readiness/providers/
    note: Provider-specific readiness checks for install and auth state; separate from runtime execution in src/harness/providers/.
  - id: codex-harness-provider-test
    type: file
    path: test/codex-harness-provider.test.ts
    note: Unit tests for the Codex app-server adapter using an in-process fake server covering approvals, structured output, timeouts, and usage parsing.
  - id: provider-boundary-plan
    type: file
    path: docs/plans/2026-05-14-provider-automation-boundary-refactor.md
    note: Records the refactor plan that separated provider runtime execution from lifecycle command and automation concerns, establishing the OperationSpec provider-neutral contract.
verified: 2026-06-03T00:00:00.000Z

---

# Harness Providers

The V1 harness layer is Almanac's provider-neutral execution boundary. Operations build one `OperationSpec`; provider adapters translate that spec to Claude, Codex, Cursor, or future runtimes and emit normalized `HarnessEvent` records for [[process-manager-runs]].

`[[src/agent/readiness/view.ts]]` is not an execution-provider layer. It builds the setup, `almanac agents`, and doctor projection from config plus provider status/model metadata. The provider-specific readiness code under `[[src/agent/readiness/providers/]]` checks CLI install/auth state and model choices; it does not own runtime execution or runtime capability metadata. Runtime execution and runtime capability metadata belong in `[[src/harness/providers/]]`.

## Provider-neutral contract

`OperationSpec` contains provider selection, `cwd`, optional system prompt, assembled prompt, base tool requests, optional helper agent specs, optional skills/MCP config, limits, output schema, and operation metadata. Provider-neutral files must not import Claude, Codex, or Cursor SDK types.

Structured output is a harness-level final-output contract, not a proposal-file pipeline. `OperationSpec.output` carries a provider-neutral `FinalOutputSpec`; the JSON Schema object is the contract, while `schemaPath` is only an optional compatibility field on the final-output type. Provider adapters must return the parsed value on `HarnessResult.output` and the `done` event instead of forcing callers to scrape final assistant prose. The implemented v1 product contract is `almanac_operation_report_v1` in `[[src/operations/reports.ts]]`, whose `summary` field is complete markdown for the sticky GitHub PR comment after `almanac ingest github:pr:<n>` runs. [@hosted-proposal-structured-output-session]

`HarnessEvent` normalizes stream output into text, tool use, tool result, tool summary, context usage, error, and done events. Tool events can carry structured display details such as kind, title, path, command, status, exit code, and duration; `jobs attach` and lifecycle commands run with `--verbose` use those fields to show activity like "Reading file" or "Running command" instead of only provider-specific tool names. Quiet foreground lifecycle jobs still log those events to JSONL, but they do not print the live tool stream to stdout. Job summaries preserve provider session id, cost, turns, and usage only when the adapter can actually supply them.

Harness history means CodeAlmanac's own job history: the `OperationSpec`, normalized `HarnessEvent` stream, `.almanac/jobs/` records, provider session id, usage, cost, status, and failure metadata produced when CodeAlmanac runs an operation. External Claude or Codex JSONL transcript stores are not harness history in this architecture. [[capture-flow]] reads those transcript stores as source material for scheduled Absorb work, but that source discovery should stay outside the harness provider contract unless the provider abstraction is deliberately expanded.

The 2026-05-28 provider-session persistence discussion added one placement rule for future harness work: whether an Almanac maintenance job should create provider-owned session history is lifecycle intent, not a provider-adapter accident. The operation layer expresses this on `OperationSpec` as `providerSession.persistence = "ephemeral" | "persistent"`, and each adapter translates that intent to its native mechanism. Claude maps ephemeral maintenance jobs to SDK `persistSession: false`, and Codex app-server maps them to `thread/start.ephemeral`. Hardcoding an ephemeral-session flag inside one adapter without a spec-level field would hide the product rule and make Build, Absorb, and Garden drift apart.

Provider session persistence is not the same problem as provider process ownership. Non-persistent maintenance sessions keep future sweeps from rediscovering Almanac's own provider-history transcripts; they do not guarantee that killing a CodeAlmanac job kills the provider CLI process and MCP children already spawned for that job. CLI-backed providers now go through the managed child process boundary in `[[src/harness/process/managed-child.ts]]`. Provider adapters ask for a managed child and call `terminate()` or `attachAbort()`; POSIX process groups are the implementation detail behind that boundary rather than a provider-facing concept. Windows provider-process cleanup is intentionally unsupported until it has a tested implementation, so provider adapters should not add their own Windows cleanup branches.

The Codex app-server adapter treats provider-process cleanup as a post-job hygiene step, not as the source of the operation result. `[[src/harness/providers/codex/app-server.ts]]` catches managed-child termination failures, emits a `HarnessEvent` error such as `Provider process cleanup failed: ...`, and still resolves the harness result that came from the provider protocol. That prevents a cleanup failure from leaving a job unresolved while still preserving the cleanup failure in `.almanac/jobs/<job-id>.jsonl`.

The harness layer is also distinct from the agent readiness code under `src/agent/readiness/`. See [[provider-lifecycle-boundary]] for the current boundary: harness providers are the execution adapter layer; readiness, auth, instruction installation, and persisted config are separate agent-support lifecycles.

## Adapters

The Claude adapter maps base tools to Claude Agent SDK tools, passes `tools` and `allowedTools`, sets `permissionMode: "dontAsk"`, supports programmatic per-job subagents, and reports cost/usage when available. Claude-specific auth and capability flags are documented in [[claude-agent-sdk]]. The adapter maps `OperationSpec.output.kind === "json_schema"` to the SDK `outputFormat` option and preserves SDK `structured_output` as `HarnessResult.output`, so Claude and Codex now share the same final-output contract. [@hosted-proposal-structured-output-session]

The Codex adapter uses `codex app-server --config mcp_servers={} --listen stdio://` with a three-phase JSON-RPC handshake: `initialize` (sends `clientInfo` and `capabilities: { experimentalApi: true }`), then `thread/start` (sets `approvalPolicy: "never"`, `sandbox: "workspace-write"`, `ephemeral` from `OperationSpec.providerSession.persistence`, and `developerInstructions` from the system prompt), then `turn/start` (sends the combined prompt as a single text input item with `sandboxPolicy: { type: "workspaceWrite", networkAccess: <bool> }`). Network access is false unless `OperationSpec.networkAccess` is true. [[src/harness/providers/codex.ts]] is now a provider facade; request construction lives in [[src/harness/providers/codex/request.ts]], JSON-RPC process handling lives in [[src/harness/providers/codex/app-server.ts]], app-server notification mapping lives in [[src/harness/providers/codex/app-notifications.ts]], harness-result projection lives in [[src/harness/providers/codex/result.ts]], and [[src/harness/providers/codex/events.ts]] is only the public compatibility facade for existing imports. Actor/subagent trace state lives in [[src/harness/providers/codex/actors.ts]], structured tool display shaping lives in [[src/harness/providers/codex/tool-display.ts]], usage parsing lives in [[src/harness/providers/codex/usage.ts]], failure classification lives in [[src/harness/providers/codex/failures.ts]], loose protocol field decoding lives in [[src/harness/providers/codex/fields.ts]], and readiness probing lives in [[src/harness/providers/codex/status.ts]]. The `mcp_servers={}` override prevents user-level Codex MCP config from leaking tools into Almanac jobs while preserving normal Codex auth. Two separate timeouts bound each job. Each of the three JSON-RPC handshake requests has a 30-second per-call timeout (default `CODEX_APP_SERVER_RPC_TIMEOUT_MS = 30_000`; overridable via env var `CODEALMANAC_CODEX_APP_SERVER_RPC_TIMEOUT_MS` for testing), guarding against a stalled or incompatible app-server at startup. After `turn/start` resolves successfully, a separate 30-minute watchdog begins (default `CODEX_APP_SERVER_TURN_TIMEOUT_MS = 30 * 60_000`; overridable via `CODEALMANAC_CODEX_APP_SERVER_TURN_TIMEOUT_MS` for testing), guarding against a model or agent that accepts the turn but never emits `turn/completed`. The two timeouts address distinct failure modes: startup unresponsiveness versus mid-execution stall. The adapter streams notifications until `turn/completed` and then kills the child process.

App-server notifications map to `HarnessEvent` as follows: `item/agentMessage/delta` -> `text_delta`; `item/plan/delta` and `turn/plan/updated` -> `tool_summary`; `item/started` and `item/completed` -> `tool_use` / `tool_result` with structured display kind (shell, edit, mcp, web, agent, read, write); `item/commandExecution/outputDelta` and `item/fileChange/outputDelta` -> `tool_summary`; `thread/tokenUsage/updated` -> `context_usage` with usage parsed from `tokenUsage.last` (per-turn counts); `turn/completed` -> terminal state; `error` notification -> `error` event. `parseCodexAppServerUsage` reads `tokenUsage.last.totalTokens` as the authoritative per-turn total, `tokenUsage.total.totalTokens` for cumulative processed tokens, and `tokenUsage.modelContextWindow` for `maxTokens` (the model's context window size).

The 2026-05-31 responsibility refactor resolved the main Codex adapter cohesion risk without changing the public harness contract. Before that change, `[[src/harness/providers/codex/events.ts]]` owned legacy JSONL event mapping, app-server notification mapping, structured tool display shaping, actor/subagent tracing, usage parsing, and failure classification. It now re-exports the stable import surface while the named Codex-provider modules own their protocol-specific responsibilities.

Server-initiated requests are handled noninteractively so lifecycle commands never block. Known response patterns: `item/commandExecution/requestApproval` and `item/fileChange/requestApproval` → `{ decision: "decline" }`; legacy `execCommandApproval` / `applyPatchApproval` → `{ decision: "denied" }`; `item/tool/requestUserInput` → `{ answers: {} }`; `mcpServer/elicitation/request` → `{ action: "decline", content: null }`; `item/tool/call` → `{ contentItems: [], success: false }`; `item/permissions/requestApproval` → `{ permissions: {}, scope: "turn", strictAutoReview: true }` (empty permission grant); `account/chatgptAuthTokens/refresh` → JSON-RPC error `-32001` (Almanac does not manage ChatGPT auth tokens). Unrecognized server requests return JSON-RPC error `-32601`.

`warning` notifications are non-terminal: the adapter maps them to `tool_summary` events (`Warning: <message>`) so a config or model warning during a turn does not fail the run. `error` notifications read the message from `params.error.message`, `params.error.detail`, or `params.message` and classify the failure via `classifyCodexFailure`.

The adapter supports model override, reasoning effort, structured output schema (passed as `outputSchema` on the turn), parsed final output, and usage reporting. Codex app-server receives the schema object directly. Per-run programmatic subagents, MCP, skills, and max-cost are unsupported and rejected at spec validation time. [@hosted-proposal-structured-output-session]

Cursor remains an explicit placeholder provider in V1. It is present in metadata as the future extension point, but runs fail clearly until a real adapter lands.

## Test coverage

The Codex adapter has a unit test suite at `test/codex-harness-provider.test.ts` backed by an in-process fake app-server. The fake server covers command approval, permission requests, explicit ChatGPT token-refresh failure, structured tool display, warning notifications, nested error notifications, token usage, turn completion, structured final output, silent app-server handshake timeout, and accepted-turn timeout. `test/claude-harness-provider.test.ts` covers the matching Claude `outputFormat` and `structured_output` path. The fake servers are permissive by design: they do not exercise a real provider turn, configured MCP tool exposure, or future provider protocol drift. End-to-end coverage requires a real provider installation.

## Capability rule

Provider metadata describes the adapter implemented here, not the provider ecosystem in general. If an adapter cannot enforce or map a field, it should reject it or mark the capability false instead of pretending the operation layer got the requested behavior.
