# Final Output Contract Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a provider-neutral structured final output contract so Almanac operations can return a typed final report for hosted GitHub PR comments without scraping prose.

**Architecture:** `AgentRunSpec.output` becomes a harness-level JSON Schema contract, `HarnessResult.output` carries the parsed final value, and operation reports define the one v1 schema plus final-output instructions. Provider adapters translate the same contract to Codex and Claude; process records persist the validated output for downstream products.

**Tech Stack:** TypeScript, raw JSON Schema objects, Codex app-server/exec structured output, Claude Agent SDK `outputFormat`, Vitest.

---

### Task 1: Harness Output Types

**Files:**
- Create: `src/harness/final-output.ts`
- Modify: `src/harness/types.ts`
- Modify: `src/harness/events.ts`
- Test: `test/harness-types.test.ts`

Add `JsonValue`, `FinalOutputSpec`, `FinalOutputResult`, `parseJsonSchemaFinalOutputText`, and helpers for text/schema results. Keep raw text for audit and expose parsed value. Keep compatibility for existing `schemaPath` callers only if needed at provider adapter boundaries.

### Task 2: Provider Mapping

**Files:**
- Modify: `src/harness/providers/codex/request.ts`
- Modify: `src/harness/providers/codex/app-server.ts`
- Modify: `src/harness/providers/codex/app-notifications.ts`
- Modify: `src/harness/providers/codex/result.ts`
- Modify: `src/harness/providers/codex/types.ts`
- Modify: `src/harness/providers/claude.ts`
- Modify: `src/harness/providers/metadata.ts`
- Test: `test/codex-harness-provider.test.ts`

Codex app-server passes `spec.output.schema`, Codex exec uses `schemaPath` only when a legacy caller supplies that adapter hint, and root final agent text is parsed into `HarnessResult.output`. Claude maps the same contract to SDK `outputFormat` and reads `structured_output` from the result message when present.

### Task 3: Operation Report Contract

**Files:**
- Create: `src/operations/reports.ts`
- Modify: `src/operations/run.ts`
- Modify: `src/ingest/context.ts`
- Test: operation/process tests as needed

Define `almanac_operation_report_v1` with `{version: 1, summary: string}` and add the two-section final-output instruction block to operation prompts when an operation report is requested. Fix GitHub ingest copy to use project knowledge / Almanac language, not memory language.

### Task 4: Process Persistence

**Files:**
- Modify: `src/process/types.ts`
- Modify: `src/process/records.ts`
- Modify: `src/process/manager.ts`
- Test: `test/process-manager.test.ts`, `test/process-records.test.ts`

Persist operation output in run records as `{version, contract, value}`. Keep `pageChanges.description` for compatibility, but prefer structured `summary` when the output contract provides one; fallback to legacy first-line summary only for runs without structured output.

### Task 5: Verification

Run:
- `npm test -- test/codex-harness-provider.test.ts test/harness-provider-registry.test.ts test/harness-types.test.ts test/process-manager.test.ts test/process-records.test.ts`
- `npm run build`
- `npm test`

Update Almanac/docs pages if the implementation changes durable harness behavior.
