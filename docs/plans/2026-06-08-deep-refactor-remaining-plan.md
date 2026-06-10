# Remaining Deep Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Finish the remaining architecture cleanup identified by the 2026-06-08 deep refactor audit after the stale connector/CLI/Codex-exec cleanup already landed on `dev`.

**Architecture:** Preserve the existing operation -> process manager -> harness provider center of gravity. The remaining refactor is not a wholesale clean-architecture rewrite; it is a sequence of boundary corrections so product facts stop flowing through rendered text, discovery code has one source model, provider identity/status has one vocabulary, read models are shared, and recovery routing stops duplicating Commander.

**Tech Stack:** TypeScript, Commander, Vitest, better-sqlite3, local filesystem records, launchd automation, Codex/Claude provider harness adapters.

---

## Baseline

Current local `dev` contains the first cleanup wave:

- `f3127e6 refactor: remove stale connector and cli surfaces`
- `a48662c refactor: remove codex exec compatibility`

Do not redo those changes. Composio, `almanac connect`, `almanac source`, stale connector runtime fields, `health --fix`, stale CLI aliases, and legacy Codex exec compatibility are already gone from local `dev`.

The main checkout has unrelated `.almanac` and audit-doc dirt. Do not stage, delete, or rewrite those files unless a later task explicitly scopes wiki/doc alignment.

Before each implementation slice, create a dedicated worktree from local `dev`:

```bash
git worktree add /Users/rohan/.config/superpowers/worktrees/codealmanac/<slice-name> -b codex/<slice-name> dev
cd /Users/rohan/.config/superpowers/worktrees/codealmanac/<slice-name>
npm install
npm run lint
npm test
```

If the baseline check fails, stop and diagnose before implementing. Each slice should be squash-merged back to `dev` after passing `npm run lint`, focused tests, full `npm test`, `npm run build`, and `git diff --check`.

## Refactor Order

Do these in order:

1. Typed lifecycle start APIs.
2. Unified capture discovery.
3. Provider readiness and identity cleanup.
4. SQLite-free CLI cleanup.
5. Wiki query read models and viewer split.
6. Health/source maintenance split.
7. Documentation/wiki alignment.

The first two are highest leverage because they remove the worst "AI slope" style boundary failures: internal state passing through rendered stdout and one product noun implemented through two different discovery models.

---

## Slice 1: Typed Lifecycle Start APIs

**Goal:** Stop `capture sweep` and lifecycle internals from depending on rendered CLI output.

**Files:**

- Create: `src/capture/start.ts`
- Create: `src/ingest/start.ts`
- Modify: `src/cli/commands/operations.ts`
- Modify: `src/cli/commands/capture-sweep.ts`
- Modify: `src/capture/sweep.ts`
- Modify: `src/operations/run.ts`
- Modify: `test/capture-sweep.test.ts`
- Modify: `test/operation-commands.test.ts`
- Modify: `test/ingest-input.test.ts`

**Target shape:**

```ts
export interface CaptureStartRequest {
  cwd: string;
  provider?: string;
  foreground: boolean;
  background: boolean;
  transcriptArgs: string[];
  captureOptions: CaptureInputOptions;
  operationOptions: OperationCommandOptions;
}

export interface CaptureStartResult {
  runId: string;
  mode: "foreground" | "background";
  recordPath?: string;
  resolvedTranscripts: ResolvedCaptureInput[];
  outcome: CommandOutcome;
}

export async function startCaptureRun(
  request: CaptureStartRequest,
): Promise<CaptureStartResult> {
  const resolved = await resolveCaptureInputs(request);
  const outcome = await runAbsorbOperation(...);
  return {
    runId: requireRunId(outcome),
    mode: request.foreground ? "foreground" : "background",
    resolvedTranscripts: resolved,
    outcome,
  };
}
```

`runCaptureCommand()` should become a thin renderer:

```ts
const result = await startCaptureRun(toCaptureStartRequest(args));
return renderOperationStartResult(result, options);
```

`capture sweep` should call `startCaptureRun()` directly and delete run-id extraction from stdout.

**Step 1: Write failing sweep test for stdout independence**

Add a regression in `test/capture-sweep.test.ts` that stubs the capture starter to return `{ runId: "run_123" }` while the renderer text is intentionally changed or absent. Assert sweep records `run_123` in the ledger without parsing stdout.

Run:

```bash
npm test -- --run test/capture-sweep.test.ts
```

Expected: fail because sweep currently calls `extractRunId(result.stdout)`.

**Step 2: Extract typed capture start**

Create `src/capture/start.ts`. Move the non-rendering capture start logic out of `runCaptureCommand()`:

- resolve capture inputs;
- choose Absorb operation;
- enqueue/run through the existing operation path;
- return typed run metadata plus the existing command outcome.

Do not duplicate operation code. The new function should call existing operation helpers.

**Step 3: Make capture command render typed result**

Modify `src/cli/commands/operations.ts` so `runCaptureCommand()` converts CLI args/options into `CaptureStartRequest`, calls `startCaptureRun()`, and renders the returned result.

Keep stdout/stderr behavior stable for users.

**Step 4: Make sweep consume typed capture result**

Modify `src/cli/commands/capture-sweep.ts` and/or `src/capture/sweep.ts` so the sweep path receives the typed starter instead of a function returning rendered `CommandOutcome`.

Delete `extractRunId()` and its regex fallback.

**Step 5: Move ingest-specific start policy**

Create `src/ingest/start.ts` for source-specific start policy that currently lives in `src/cli/commands/operations.ts`, especially GitHub PR sticky-comment output selection.

Target:

```ts
export async function startIngestRun(request: IngestStartRequest): Promise<IngestStartResult> {
  const input = await resolveIngestInput(...);
  const output = chooseIngestOutputContract(input);
  const outcome = await runAbsorbOperation({ output, networkAccess: input.kind === "source" });
  return { input, outcome, runId: requireRunId(outcome) };
}
```

The CLI should render; ingest should decide source output contracts.

**Step 6: Replace message-substring lifecycle error classification**

Introduce typed errors in the lifecycle start layer:

```ts
export class MissingWikiError extends Error {
  readonly code = "missing_wiki";
}

export class SourceResolutionError extends Error {
  readonly code = "source_resolution_failed";
}
```

Render typed errors in command adapters instead of checking message substrings such as `"no .almanac/"`.

**Step 7: Verify focused behavior**

Run:

```bash
npm test -- --run test/capture-sweep.test.ts test/operation-commands.test.ts test/ingest-input.test.ts test/absorb-operation.test.ts
npm run lint
```

Expected: all pass.

**Step 8: Commit slice**

```bash
git add src/capture/start.ts src/ingest/start.ts src/cli/commands/operations.ts src/cli/commands/capture-sweep.ts src/capture/sweep.ts src/operations/run.ts test/capture-sweep.test.ts test/operation-commands.test.ts test/ingest-input.test.ts test/absorb-operation.test.ts
git commit -m "refactor: add typed lifecycle start APIs"
```

---

## Slice 2: Unified Capture Discovery

**Goal:** Make manual capture and scheduled sweep use the same session candidate model.

**Files:**

- Modify: `src/capture/input.ts`
- Modify: `src/capture/discovery/index.ts`
- Modify: `src/capture/discovery/types.ts`
- Modify: `src/capture/discovery/jsonl.ts`
- Modify: `src/capture/discovery/claude.ts`
- Modify: `src/capture/discovery/codex.ts`
- Modify: `src/capture/start.ts`
- Modify: `src/capture/sweep.ts`
- Modify: `test/capture-sweep.test.ts`
- Modify: `test/operation-commands.test.ts`

**Target shape:**

```ts
const candidates = await discoverSessionCandidates({
  apps,
  cwd,
  since,
  includeAllApps,
});

const selected = manualCapturePolicy.select(candidates, {
  explicitPaths,
  app,
  limit,
});

const eligible = sweepPolicy.selectQuietEligible(candidates, {
  quietWindow,
  ledger,
});
```

Manual capture and sweep may choose differently. They should not scan different stores through different parsers.

**Step 1: Add failing manual Codex capture test**

In `test/operation-commands.test.ts`, add a test for `almanac capture --app codex` with a fake Codex transcript candidate. Assert manual capture can resolve a Codex candidate without explicit file paths.

Expected: fail because manual capture currently rejects non-Claude app discovery.

**Step 2: Add shared manual selection policy**

In `src/capture/input.ts` or a new `src/capture/manual-selection.ts`, implement selection over `SessionCandidate`:

```ts
export function selectManualCaptureCandidates(
  candidates: SessionCandidate[],
  options: ManualCaptureSelectionOptions,
): SessionCandidate[] {
  return candidates
    .filter(matchesRequestedApp)
    .sort(byLatestActivity)
    .slice(0, options.limit ?? 1);
}
```

Keep explicit transcript file support.

**Step 3: Replace Claude-only fallback**

Replace directory/content matching in `src/capture/input.ts` with shared discovery helpers. If a head read is still needed for explicit files, use the bounded-read helper from `src/capture/discovery/jsonl.ts`, not `readFile().slice()`.

**Step 4: Decide `--all-apps` behavior**

Support `capture --all-apps` through shared discovery. If that creates unclear manual semantics, narrow it to "search all apps and choose latest candidate" and document that in tests.

**Step 5: Preserve sweep behavior**

Run existing sweep tests after manual discovery changes. Sweep quiet-window, ledger pending reconciliation, and skip reasons should not change.

**Step 6: Verify**

```bash
npm test -- --run test/capture-sweep.test.ts test/operation-commands.test.ts
npm run lint
```

**Step 7: Commit**

```bash
git add src/capture test/capture-sweep.test.ts test/operation-commands.test.ts
git commit -m "refactor: unify capture discovery"
```

---

## Slice 3: Provider Readiness And Identity Cleanup

**Goal:** Create one provider identity vocabulary and remove prose parsing from readiness/status logic.

**Files:**

- Create: `src/agent/provider-id.ts` or `src/providers.ts`
- Modify: `src/config/providers.ts`
- Modify: `src/harness/types.ts`
- Modify: `src/harness/providers/metadata.ts`
- Modify: `src/agent/readiness/types.ts`
- Modify: `src/agent/readiness/view.ts`
- Modify: `src/agent/readiness/providers/status.ts`
- Modify: `src/agent/readiness/providers/claude/index.ts`
- Modify: `src/agent/readiness/providers/codex-cli.ts`
- Modify: `src/agent/readiness/providers/cursor-cli.ts`
- Modify: `src/cli/commands/doctor/agents.ts`
- Modify: `src/cli/commands/setup/agent-choice.ts`
- Modify: `src/process/spec.ts`
- Modify: `src/process/records.ts`
- Modify: `src/harness/events.ts`
- Modify: `src/harness/providers/codex/tool-display.ts`
- Modify: `src/harness/providers/codex/failures.ts`
- Modify: `src/harness/providers/codex/app-server.ts`
- Modify: relevant provider/readiness/Codex/process-log tests.

**Target shape:**

```ts
export type ProviderId = "claude" | "codex" | "cursor";

export const PROVIDERS: Record<ProviderId, {
  id: ProviderId;
  displayName: string;
  defaultModel: string;
}> = { ... };

export function isProviderId(value: unknown): value is ProviderId { ... }
```

Readiness status should be structured:

```ts
export interface ProviderReadinessStatus {
  id: ProviderId;
  installed: boolean;
  authenticated: boolean;
  readiness: "ready" | "missing_executable" | "not_authenticated" | "unknown";
  accountLabel?: string;
  detail: string;
  installFix?: string;
  loginFix?: string;
}
```

**Step 1: Add identity consistency tests**

Add or update tests so setup, agents, process spec validation, records, and harness metadata agree on provider ids/default display labels.

Run focused tests and confirm failure where duplicate catalogs drift or tests need new API.

**Step 2: Add shared provider identity module**

Create `src/agent/provider-id.ts` or `src/providers.ts`. Prefer the smallest location that does not imply runtime ownership. Move `ALL_AGENT_PROVIDER_IDS`, id guards, display names, and default models there.

Update imports in config, harness, process records/spec, setup, and tests.

**Step 3: Rename readiness types**

Rename readiness provider types to avoid "runtime provider" confusion:

```ts
AgentProviderStatus -> ProviderReadinessStatus
AgentProviderMetadata -> ProviderReadinessMetadata
```

Do not move runtime adapters out of `src/harness/providers/`.

**Step 4: Stop parsing readiness prose**

Modify readiness providers to return `readiness`, `accountLabel`, `installFix`, and `loginFix`. Make `src/agent/readiness/view.ts` consume those fields without regexing `detail`.

**Step 5: Remove doctor injected provider branch**

Delete `injectedProviderStatuses()` from `src/cli/commands/doctor/agents.ts`. Pass `spawnCli` through `listProviderStatuses(spawnCli)` so doctor tests exercise the same readiness provider catalog.

**Step 6: Remove nested `display.raw` from persisted harness events**

Remove `raw?: unknown` from `HarnessToolDisplay`. Update Codex tool display mapping to preserve only normalized fields.

If thread/turn ids are still needed, add explicit fields:

```ts
providerThreadId?: string;
providerTurnId?: string;
```

Update process-log and viewer-job tests to assert no nested raw provider payload persists.

**Step 7: Prefer structured Codex error classification**

Change `classifyCodexFailure()` to accept a structured error input:

```ts
type CodexFailureInput = {
  message: string;
  code?: number;
  data?: unknown;
  statusCode?: number;
};
```

Keep string parsing only as fallback for unstructured stderr.

**Step 8: Verify**

```bash
npm test -- --run test/provider-view.test.ts test/agents-command.test.ts test/doctor.test.ts test/harness-types.test.ts test/harness-provider-registry.test.ts test/process-logs.test.ts test/codex-harness-provider.test.ts
npm run lint
```

**Step 9: Commit**

```bash
git add src test
git commit -m "refactor: normalize provider readiness and identity"
```

---

## Slice 4: SQLite-Free CLI Cleanup

**Goal:** Delete or sharply shrink the hand-written parser in `src/cli/sqlite-free.ts` while preserving recovery commands when native SQLite is broken.

**Files:**

- Modify: `bin/codealmanac.ts`
- Modify: `src/cli.ts`
- Modify: `src/cli/register-query-commands.ts`
- Modify: `src/cli/register-edit-commands.ts`
- Modify: `src/cli/register-setup-commands.ts`
- Modify: `src/cli/register-wiki-lifecycle-commands.ts`
- Modify: `src/cli/sqlite-free.ts`
- Modify: `test/launcher-runtime.test.ts`
- Modify: `test/cli.test.ts`
- Modify: `test/setup.test.ts`
- Modify: `test/doctor.test.ts`
- Modify: `test/automation.test.ts`
- Modify: `test/uninstall.test.ts`
- Modify: `test/update.test.ts`

**Target shape:**

Registration files should not import SQLite-heavy command implementations at module load. Command actions should lazy-import implementations:

```ts
program
  .command("search [query]")
  .action(async (...args) => {
    const { runSearchCommand } = await import("./commands/search.js");
    return runSearchCommand(...args);
  });
```

If a separate sqlite-free file remains, it should only handle truly pre-Commander recovery cases and document why.

**Step 1: Add broken-SQLite import tests**

Add tests that simulate `better-sqlite3` load failure and assert these commands still work:

- `almanac setup --help`
- `almanac doctor`
- `almanac update --check`
- `almanac uninstall --help`
- `almanac automation status`

Expected before implementation: at least some imports still require sqlite-heavy modules or sqlite-free parser coverage is too broad.

**Step 2: Audit command registration imports**

For each `src/cli/register-*.ts`, identify top-level imports that pull command modules which import `src/wiki/indexer/*` or `better-sqlite3`.

Move those imports inside action handlers.

**Step 3: Shrink `sqlite-free.ts`**

After registration is safe, remove duplicated setup/automation/config parsing from `src/cli/sqlite-free.ts`. Keep only the minimum emergency path if needed by `bin/codealmanac.ts`.

**Step 4: Preserve help and shortcut behavior**

Run help-output tests. If setup shortcut behavior still needs pre-Commander handling, keep that one path explicit in `src/cli.ts` with a comment explaining the native-binding failure case.

**Step 5: Verify**

```bash
npm test -- --run test/launcher-runtime.test.ts test/cli.test.ts test/setup.test.ts test/doctor.test.ts test/automation.test.ts test/uninstall.test.ts test/update.test.ts
npm run lint
```

**Step 6: Commit**

```bash
git add bin/codealmanac.ts src/cli.ts src/cli test
git commit -m "refactor: simplify sqlite-free cli recovery"
```

---

## Slice 5: Wiki Query Read Models And Viewer Split

**Goal:** Move shared read projections out of CLI/viewer modules and admit the viewer's actual product scope.

**Files:**

- Create: `src/wiki/query/pages.ts`
- Create: `src/wiki/query/topics.ts`
- Modify: `src/wiki/query/search.ts`
- Modify: `src/cli/commands/search.ts`
- Modify: `src/cli/commands/topics/list.ts`
- Modify: `src/cli/commands/topics/show.ts`
- Modify: `src/cli/commands/topics/read.ts`
- Modify: `src/viewer/api.ts`
- Create: `src/viewer/wiki-api.ts`
- Create: `src/viewer/jobs-api.ts`
- Create: `src/viewer/review-api.ts`
- Create: `src/viewer/global-api.ts` if not already split enough
- Modify: `src/viewer/server.ts`
- Modify: `src/cli/commands/serve.ts`
- Modify: viewer/CLI query tests.

**Target shape:**

```ts
// src/wiki/query/pages.ts
export interface PageSummary { ... }
export function recentPages(db, options): PageSummary[] { ... }
export function searchPages(db, options): PageSummary[] { ... }
export function pagesMentioningPath(db, path, options): PageSummary[] { ... }

// src/wiki/query/topics.ts
export function topicSummaries(db, options): TopicSummary[] { ... }
export function topicDetail(db, slug, options): TopicDetail | null { ... }
export function pagesForTopicSubtree(db, slug, options): PageSummary[] { ... }
```

`src/viewer/server.ts` composes APIs. `almanac serve` help should say either "local Almanac console" or be scoped down to current wiki. Recommended decision: call it local console, because it already exposes global registry/jobs/review behavior.

**Step 1: Add projection consistency tests**

Add tests asserting CLI and viewer agree on:

- archive filters;
- topic counts;
- file mention semantics;
- page summary slugs/titles/topics;
- topic subtree page membership.

Use existing fixtures from `test/helpers.ts`.

**Step 2: Extract page projections**

Move recent/search/mentions/page-summary SQL into `src/wiki/query/pages.ts`. Keep FTS expression construction configurable so CLI and viewer can keep different search UX.

**Step 3: Extract topic projections**

Move topic list/detail/page-list SQL into `src/wiki/query/topics.ts`. Keep topic DAG storage and mutation in `src/wiki/topics/`.

**Step 4: Update CLI commands**

Change `search` and `topics` commands to call the query functions and render results only.

**Step 5: Split viewer API**

Break `src/viewer/api.ts` into route-specific modules. Keep `server.ts` as the composer.

**Step 6: Update serve scope docs/help**

If keeping global console behavior, update help text to avoid implying "current wiki only."

**Step 7: Verify**

```bash
npm test -- --run test/search.test.ts test/search-stderr.test.ts test/topics.test.ts test/viewer-api.test.ts test/viewer-global-api.test.ts test/viewer-routes.test.ts test/serve-command.test.ts
npm run lint
```

**Step 8: Commit**

```bash
git add src/wiki/query src/cli/commands/search.ts src/cli/commands/topics src/viewer src/cli/commands/serve.ts test
git commit -m "refactor: share wiki query read models"
```

---

## Slice 6: Health And Source Maintenance Split

**Goal:** Keep health as diagnosis/report composition and move source/citation checks plus legacy source migration into source maintenance modules.

**Files:**

- Create: `src/wiki/sources/health.ts`
- Create: `src/wiki/sources/maintenance.ts`
- Modify: `src/wiki/health/index.ts`
- Move/delete: `src/wiki/health/legacy-frontmatter-fix.ts`
- Modify: `src/cli/commands/migrate.ts`
- Modify: `test/health.test.ts`
- Modify: `test/migrate-command.test.ts`

**Target shape:**

```ts
// src/wiki/sources/health.ts
export function collectSourceHealthFindings(...): SourceHealthFindings { ... }

// src/wiki/sources/maintenance.ts
export function migrateLegacySourceFrontmatter(...): MigrationResult { ... }

// src/wiki/health/index.ts
export function collectHealthReport(...) {
  return composeHealthReport({
    graph: collectGraphFindings(...),
    sources: collectSourceHealthFindings(...),
  });
}
```

`health` reports. `migrate legacy-sources` mutates. Do not reintroduce `health --fix`.

**Step 1: Add migration boundary test**

Assert `almanac health` reports migration-needed warnings but has no mutating option. Assert `almanac migrate legacy-sources` calls the maintenance function and rewrites only legacy source frontmatter.

**Step 2: Move source/citation health helpers**

Move source/citation parsing and checks out of `src/wiki/health/index.ts`.

**Step 3: Move legacy migration writer**

Move `legacy-frontmatter-fix.ts` into `src/wiki/sources/maintenance.ts` or re-export from there if a small compatibility step is needed.

**Step 4: Reuse frontmatter parser**

For empty-page detection, use `parseFrontmatter(raw).body` instead of a separate regex.

**Step 5: Verify**

```bash
npm test -- --run test/health.test.ts test/migrate-command.test.ts test/frontmatter.test.ts
npm run lint
```

**Step 6: Commit**

```bash
git add src/wiki/sources src/wiki/health src/cli/commands/migrate.ts test/health.test.ts test/migrate-command.test.ts test/frontmatter.test.ts
git commit -m "refactor: split source maintenance from health"
```

---

## Slice 7: Documentation And Wiki Alignment

**Goal:** Align public docs, repo instructions, and active wiki pages with the final architecture.

**Files:**

- Modify: `MANUAL.md`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md` if present in branch
- Modify: `guides/reference.md`
- Modify: relevant `.almanac/pages/*.md`
- Modify: `docs/architecture-audit-2026-06-08/refactor-roadmap.md` only if this audit folder is being committed.

**Required wording updates:**

- Replace "only capture and bootstrap touch AI/write pages" with:

```text
Only lifecycle operations invoke AI or write page prose. Read commands may refresh derived local index state and read committed markdown for display or validation. Organization commands may deterministically rewrite wiki metadata through explicit verbs such as tag, topics, review, and migrate.
```

- State that GitHub source ingest uses local `gh` in the OSS CLI.
- State that `migrate legacy-sources` is the explicit mutation path for legacy source frontmatter.
- State that Codex runtime is app-server-backed and SDK is not adopted because it lacks ephemeral/process/actor controls.
- State the runtime/readiness provider split with current file names.
- State whether `almanac serve` is a local console or current-wiki viewer.

**Step 1: Search stale docs**

Run:

```bash
rg -n "Composio|health --fix|capture status|almanac ps|show --raw|bootstrap|codex exec|connect github|source github|Codex SDK|app-server|only .* capture" MANUAL.md AGENTS.md CLAUDE.md guides docs .almanac/pages
```

Review each hit. Do not rewrite historical plans unless the stale text is likely to mislead future implementation work.

**Step 2: Update active instructions**

Patch active repo instruction files first. Keep wording precise and not aspirational.

**Step 3: Update active wiki pages**

Patch only pages where code truth has changed. Include exact files in frontmatter/sources if the wiki convention requires it.

Do not delete `.almanac` pages. Do not rewrite audit docs unless needed.

**Step 4: Verify docs**

Run:

```bash
rg -n "Composio|health --fix|capture status|almanac ps|show --raw|bootstrap|codex exec|connect github|source github" MANUAL.md AGENTS.md CLAUDE.md guides .almanac/pages
git diff --check
```

Expected: remaining hits are either historical context or explicitly marked as removed history.

**Step 5: Commit**

```bash
git add MANUAL.md AGENTS.md CLAUDE.md guides/reference.md .almanac/pages docs/architecture-audit-2026-06-08
git commit -m "docs: align architecture instructions after refactor"
```

Only include `.almanac` pages in this commit if the user explicitly wants wiki alignment committed. The current working tree already has unrelated `.almanac` changes, so this slice should probably run in a clean worktree and patch only intentional wiki pages.

---

## Final Verification For Each Slice

Before merging a slice to `dev`, run:

```bash
npm run lint
npm test
npm run build
git diff --check
```

After squash-merging to `dev`, rerun:

```bash
npm run lint
npm test
npm run build
git status --short --branch
```

The main `dev` checkout may still show unrelated `.almanac` or audit-doc changes. That is acceptable only if the committed slice paths are clean and the unrelated files were not staged.

## PR / Merge Policy

Each slice should be one branch and one squash commit on `dev`.

Recommended branch names:

- `codex/lifecycle-start-boundary`
- `codex/unified-capture-discovery`
- `codex/provider-readiness-cleanup`
- `codex/sqlite-free-cli-cleanup`
- `codex/wiki-query-viewer-split`
- `codex/source-health-maintenance`
- `codex/refactor-doc-alignment`

Recommended commit messages:

- `refactor: add typed lifecycle start APIs`
- `refactor: unify capture discovery`
- `refactor: normalize provider readiness and identity`
- `refactor: simplify sqlite-free cli recovery`
- `refactor: share wiki query read models`
- `refactor: split source maintenance from health`
- `docs: align architecture instructions after refactor`

## Stop Conditions

Stop and ask before implementing if any of these happen:

- A slice requires changing user-facing behavior not named in this plan.
- A migration touches `.almanac` page prose rather than deterministic metadata.
- A provider cleanup would remove current Claude/Codex runtime capability.
- `sqlite-free.ts` cannot be simplified without losing broken-SQLite recovery.
- Viewer scope requires a product decision different from "local Almanac console."

## Current Confidence

- Overall direction: high.
- Slice 1 value: very high.
- Slice 2 value: high.
- Slice 3 value: medium-high.
- Slice 4 risk: medium, because native-binding failure behavior is subtle.
- Slice 5 risk: medium, because SQL projection changes can create small semantic drift.
- Slice 6 value: medium, mostly prevents future accumulation.
- Slice 7 value: high after code settles, but should not be mixed with source changes unless the exact docs are scoped.
