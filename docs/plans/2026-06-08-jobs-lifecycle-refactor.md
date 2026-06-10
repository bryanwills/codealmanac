# Jobs Lifecycle Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rename and reshape the current `process`/`run` lifecycle into a coherent `jobs` subsystem while preserving old local `.almanac/runs/` history through an explicit compatibility path.

**Architecture:** Operations define semantic work (`build`, `absorb`, `garden`); jobs own one queued/executed lifecycle instance of that work; harness providers execute the provider runtime; OS child-process control lives near the harness, not in jobs. The final vocabulary is `JobRecord`, `JobSpec`, `JobStatus`, `jobId`, `.almanac/jobs/`, and `src/jobs/`; old `run_*` records and `.almanac/runs/` are read/migrated as compatibility only.

**Tech Stack:** TypeScript, Vitest, Node filesystem APIs, Commander CLI, local `.almanac/` filesystem state, existing harness providers.

---

## Non-Negotiables

- Start from a clean `dev` worktree. Do not use the dirty main checkout.
- Do not delete or rewrite `.almanac/` wiki pages or architecture-audit docs.
- Keep `almanac jobs` as the user-facing command.
- Keep operation names `build`, `absorb`, and `garden`.
- Use `git mv` for file moves where possible.
- Do not introduce a workflow engine, command bus, class hierarchy, or state-machine library.
- Preserve old local job history:
  - New jobs write to `.almanac/jobs/`.
  - Old `.almanac/runs/` records are migrated or read by fallback.
  - Old `run_*` ids remain valid for lookup/cancel/show/logs.
  - New ids use `job_*`.
- Keep `__run-worker` as a hidden compatibility alias for one release; new background starts should spawn `__job-worker`.

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `almanac show process-manager-runs`
- `almanac show lifecycle-architecture`
- `almanac show provider-lifecycle-boundary`
- `src/process/manager.ts`
- `src/process/background.ts`
- `src/process/records.ts`
- `src/process/spec.ts`
- `src/process/logs.ts`
- `src/cli/commands/jobs.ts`
- `src/viewer/jobs.ts`
- `src/viewer/job-projections.ts`
- `src/harness/types.ts`

## Target Shape

```text
src/operations/
  spec.ts              # OperationKind, OperationSpec, ProviderSessionPersistence
  output.ts            # operation-specific output summarization
  build.ts
  absorb.ts
  garden.ts
  run.ts

src/jobs/
  index.ts
  ids.ts
  start.ts             # foreground/background public entrypoints
  worker.ts            # queued worker drain
  executor.ts          # execute one claimed job
  events.ts            # log event sink + observer fanout + providerSessionId persistence
  finalization.ts      # done/failed/cancelled terminal writes
  wiki-effects.ts      # snapshots, page deltas, summary counts, reindex-on-success
  output.ts            # neutral final output -> JobOperationOutput
  records.ts
  logs.ts
  spec.ts
  queue.ts
  snapshots.ts
  projections/
    log-events.ts
    agent-traces.ts
    warnings.ts
  types.ts

src/harness/process/
  managed-child.ts     # actual OS child-process group management
```

Call flow:

```ts
const spec = await createGardenOperationSpec(...);
const result = await startForegroundJob({ repoRoot, spec });
```

Execution flow:

```ts
startForegroundJob(...)
  -> claim foreground job under per-wiki worker lock
  -> executeClaimedJob(...)

startBackgroundJob(...)
  -> write JobSpec
  -> write queued JobRecord
  -> initialize Job log
  -> spawn __job-worker

runJobWorker(...)
  -> acquire worker lock
  -> oldestQueuedJob(...)
  -> readJobSpec(...)
  -> startQueuedJob(...)

executeClaimedJob(...)
  -> snapshotWikiBeforeJob(...)
  -> run harness provider with createJobEventSink(...)
  -> computeJobWikiEffect(...)
  -> projectJobOutput(...)
  -> summarizeOperationOutput(...)
  -> finalizeJobUnlessCancelled(...)
```

---

## Task 1: Move Provider Child-Process Control To Harness

**Files:**
- Move: `src/process/managed-child.ts` -> `src/harness/process/managed-child.ts`
- Modify: `src/harness/providers/claude.ts`
- Modify: `src/harness/providers/codex/app-server.ts`
- Modify: `src/process/index.ts`
- Modify: `test/managed-child.test.ts`
- Modify: `test/claude-harness-provider.test.ts`
- Modify: `test/codex-harness-provider.test.ts`

**Step 1: Write/adjust import expectations**

Update `test/managed-child.test.ts` to import:

```ts
import { spawnManagedChildProcess } from "../src/harness/process/managed-child.js";
```

**Step 2: Run the focused test to verify current imports fail**

Run:

```bash
npx vitest run test/managed-child.test.ts
```

Expected: fail until the file move/import changes are done.

**Step 3: Move the file and update imports**

Run:

```bash
mkdir -p src/harness/process
git mv src/process/managed-child.ts src/harness/process/managed-child.ts
```

Update production imports:

```ts
// src/harness/providers/claude.ts
import { spawnManagedChildProcess } from "../process/managed-child.js";

// src/harness/providers/codex/app-server.ts
import { spawnManagedChildProcess } from "../../process/managed-child.js";
```

Remove the managed-child export from `src/process/index.ts`.

**Step 4: Verify**

Run:

```bash
npm run lint
npx vitest run test/managed-child.test.ts test/claude-harness-provider.test.ts test/codex-harness-provider.test.ts
```

Expected: pass.

**Step 5: Commit**

```bash
git add src/harness/process src/harness/providers src/process/index.ts test
git commit -m "refactor: move provider process control into harness"
```

---

## Task 2: Move Lifecycle Module From `process` To `jobs`

This task is a location-only move. Do not rename types/functions yet.

**Files:**
- Move: `src/process/` -> `src/jobs/`
- Modify imports across `src/` and `test/`
- Modify: `src/cli.ts`

**Step 1: Move the directory**

Run:

```bash
git mv src/process src/jobs
```

**Step 2: Update imports**

Use `rg` first:

```bash
rg -n "../process|../../process|src/process|from \"\\.\\/process|from \"\\.\\.\\/process" src test
```

Update imports to `jobs`.

Examples:

```ts
// Before
import { listRunRecords } from "../process/index.js";

// After
import { listRunRecords } from "../jobs/index.js";
```

Update `src/cli.ts` hidden worker import path if it imports from `process`.

**Step 3: Verify**

Run:

```bash
npm run lint
npx vitest run test/process-records.test.ts test/process-manager.test.ts test/process-background.test.ts test/process-queue.test.ts test/jobs-command.test.ts test/viewer-api.test.ts test/sync.test.ts
```

Expected: pass. Test filenames may still contain `process` at this point.

**Step 4: Commit**

```bash
git add -A src test
git commit -m "refactor: move lifecycle code under jobs"
```

---

## Task 3: Rename Run Vocabulary To Job Vocabulary

**Files:**
- Modify: `src/jobs/types.ts`
- Modify: `src/jobs/ids.ts`
- Modify: `src/jobs/records.ts`
- Modify: `src/jobs/logs.ts`
- Modify: `src/jobs/spec.ts`
- Modify: `src/jobs/queue.ts`
- Modify: `src/jobs/start.ts` or current manager/background files
- Modify: `src/jobs/index.ts`
- Rename tests:
  - `test/process-records.test.ts` -> `test/jobs-records.test.ts`
  - `test/process-manager.test.ts` -> `test/jobs-executor.test.ts`
  - `test/process-background.test.ts` -> `test/jobs-worker.test.ts`
  - `test/process-queue.test.ts` -> `test/jobs-queue.test.ts`
  - `test/process-logs.test.ts` -> `test/jobs-logs.test.ts`
  - `test/process-snapshots.test.ts` -> `test/jobs-snapshots.test.ts`

**Step 1: Rename types**

Use these final names:

```ts
RunStatus -> JobStatus
DisplayRunStatus -> DisplayJobStatus
RunSummary -> JobSummary
RunPageChanges -> JobPageChanges
RunOperationOutput -> JobOperationOutput
RunRecord -> JobRecord
RunView -> JobView
RunLogEntry -> JobLogEntry
RunLogEntryV1 -> JobLogEntryV1
RunLogEntryV2 -> JobLogEntryV2
```

**Step 2: Rename functions**

Use these final names:

```ts
createRunId -> createJobId
runsDir -> jobsDir
runRecordPath -> jobRecordPath
runLogPath -> jobLogPath
runCancelPath -> jobCancelPath
markRunCancelled -> markJobCancelled
isRunCancellationRequested -> isJobCancellationRequested
writeRunRecord -> writeJobRecord
readRunRecord -> readJobRecord
listRunRecords -> listJobRecords
buildStartedRunRecord -> buildStartedJobRecord
buildQueuedRunRecord -> buildQueuedJobRecord
finishRunRecord -> finishJobRecord
isRunRecord -> isJobRecord
toRunView -> toJobView
runSpecPath -> jobSpecPath
writeRunSpec -> writeJobSpec
readRunSpec -> readJobSpec
startForegroundProcess -> startForegroundJob
startQueuedProcess -> startQueuedJob
startBackgroundProcess -> startBackgroundJob
runBackgroundWorker -> runJobWorker
oldestQueuedRun -> oldestQueuedJob
runWorkerLockPath -> jobWorkerLockPath
acquireRunWorkerLock -> acquireJobWorkerLock
```

`jobsDir()` may temporarily continue pointing at `.almanac/runs/` until Task 4. If so, add a short comment saying storage migration happens in Task 4; do not leave that comment after Task 4.

Return fields should become `jobId`, not `runId`:

```ts
export interface StartJobResult {
  jobId: string;
  record: JobRecord;
  result: HarnessResult;
}
```

**Step 3: Keep operation field unchanged**

Do not rename:

```ts
record.operation
OperationKind = "build" | "absorb" | "garden"
```

**Step 4: Verify no old source vocabulary remains**

Run:

```bash
rg -n "RunRecord|RunStatus|RunView|RunSummary|RunPageChanges|RunOperationOutput|startForegroundProcess|startQueuedProcess|startBackgroundProcess|runRecordPath|runLogPath|runsDir|listRunRecords|readRunRecord|writeRunRecord|process/index" src test
```

Expected: no matches except explicit legacy compatibility comments added in later tasks. At this stage, there should be no matches.

**Step 5: Verify**

Run:

```bash
npm run lint
npx vitest run test/jobs-records.test.ts test/jobs-executor.test.ts test/jobs-worker.test.ts test/jobs-queue.test.ts test/jobs-command.test.ts test/viewer-api.test.ts test/sync.test.ts
```

Expected: pass.

**Step 6: Commit**

```bash
git add -A src test
git commit -m "refactor: rename run lifecycle to jobs"
```

---

## Task 4: Introduce `.almanac/jobs/` Storage With Legacy `.almanac/runs/` Compatibility

**Files:**
- Modify: `src/jobs/ids.ts`
- Modify: `src/jobs/records.ts`
- Modify: `src/jobs/spec.ts`
- Modify: `src/jobs/queue.ts`
- Modify: `src/jobs/logs.ts`
- Modify: `src/cli/commands/jobs.ts`
- Modify: `src/viewer/jobs.ts`
- Modify: `test/jobs-records.test.ts`
- Modify: `test/jobs-command.test.ts`
- Modify: `test/viewer-api.test.ts`
- Modify: `test/sync.test.ts`

**Step 1: Add failing tests**

Add tests covering:

```ts
it("writes new job records to .almanac/jobs with job_ ids", async () => {
  const id = createJobId(new Date("2026-06-08T12:00:00.000Z"));
  expect(id).toMatch(/^job_20260608120000_[0-9a-f]{8}$/);
  expect(jobRecordPath(repo, id)).toContain(".almanac/jobs/");
});
```

```ts
it("lists legacy .almanac/runs records as jobs", async () => {
  // Write run_*.json under .almanac/runs.
  // listJobRecords(repo) should include it.
});
```

```ts
it("resolves old run ids for jobs show/logs/cancel compatibility", async () => {
  // Write run_*.json and run_*.jsonl under .almanac/runs.
  // run `almanac jobs show run_...` through command helper.
  // Expected: old record is found.
});
```

**Step 2: Implement primary and legacy paths**

In `src/jobs/records.ts`, change `jobsDir()` to the primary new storage path and add `legacyRunsDir()`:

```ts
export function jobsDir(repoRoot: string): string {
  return join(getRepoAlmanacDir(repoRoot), "jobs");
}

export function legacyRunsDir(repoRoot: string): string {
  return join(getRepoAlmanacDir(repoRoot), "runs");
}
```

New path helpers must return `.almanac/jobs/`:

```ts
export function jobRecordPath(repoRoot: string, jobId: string): string {
  return join(jobsDir(repoRoot), `${jobId}.json`);
}
```

Add resolver helpers for user-supplied ids:

```ts
export async function resolveJobRecordPath(
  repoRoot: string,
  jobId: string,
): Promise<string> {
  const primary = jobRecordPath(repoRoot, jobId);
  if (existsSync(primary)) return primary;
  const legacy = join(legacyRunsDir(repoRoot), `${jobId}.json`);
  if (existsSync(legacy)) return legacy;
  return primary;
}
```

Do the same for logs, specs, and cancel marker paths.

**Step 3: Implement migration**

Add:

```ts
export async function migrateLegacyRunsStorage(repoRoot: string): Promise<void>
```

Rules:

- If `.almanac/jobs/` does not exist and `.almanac/runs/` exists, rename `.almanac/runs/` to `.almanac/jobs/`.
- If both exist, do not merge automatically. Read both for compatibility.
- Preserve old `run_*` ids and record contents. Do not rewrite JSONL event envelopes in this task.

Call migration from:

```ts
listJobRecords(repoRoot)
startBackgroundJob(...)
startForegroundJob(...)
runJobWorker(...)
```

**Step 4: Accept both id prefixes**

Update record validation:

```ts
function isJobId(value: string): boolean {
  return value.startsWith("job_") || value.startsWith("run_");
}
```

Update viewer/CLI safe-id validation to accept both:

```ts
/^(job|run)_[A-Za-z0-9_-]+$/
```

New jobs must use `job_*`; old `run_*` is compatibility only.

**Step 5: Verify**

Run:

```bash
npm run lint
npx vitest run test/jobs-records.test.ts test/jobs-command.test.ts test/viewer-api.test.ts test/sync.test.ts
```

Expected: pass.

**Step 6: Commit**

```bash
git add -A src test
git commit -m "refactor: store lifecycle jobs under almanac jobs"
```

---

## Task 5: Rename Hidden Worker Command With Compatibility Alias

**Files:**
- Modify: `src/cli.ts`
- Modify: `src/jobs/worker.ts` or current background module
- Modify: `test/jobs-worker.test.ts`
- Modify: `test/cli.test.ts` if it covers hidden worker routing

**Step 1: Add failing test**

Update existing background spawn test:

```ts
expect(spawned.args).toContain("__job-worker");
```

Add compatibility test:

```ts
// invoke CLI hidden dispatch with ["__run-worker"]
// Expected: routes to runJobWorker for compatibility.
```

**Step 2: Implement**

New background jobs spawn:

```ts
args: [entrypoint, "__job-worker"]
```

CLI dispatch accepts both:

```ts
if (args[0] === "__job-worker" || args[0] === "__run-worker") {
  await runJobWorker(...);
}
```

Add a comment:

```ts
// Compatibility: old background workers may still invoke __run-worker.
```

**Step 3: Verify**

Run:

```bash
npm run lint
npx vitest run test/jobs-worker.test.ts test/cli.test.ts
```

Expected: pass.

**Step 4: Commit**

```bash
git add src/cli.ts src/jobs test
git commit -m "refactor: rename hidden worker command to job worker"
```

---

## Task 6: Move Operation Spec Ownership Out Of Harness

**Files:**
- Create: `src/operations/spec.ts`
- Modify: `src/harness/types.ts`
- Modify: `src/harness/index.ts`
- Modify: `src/jobs/spec.ts`
- Modify: `src/jobs/types.ts`
- Modify: `src/operations/run.ts`
- Modify: `src/operations/build.ts`
- Modify: `src/operations/absorb.ts`
- Modify: `src/operations/garden.ts`
- Modify provider tests importing `AgentRunSpec`

**Step 1: Add new spec module**

Create:

```ts
// src/operations/spec.ts
import type { FinalOutputSpec } from "../harness/final-output.js";
import type { ToolRequest } from "../harness/tools.js";
import type { AgentProviderId } from "../agent/provider-id.js";

export type OperationKind = "build" | "absorb" | "garden";
export type ProviderSessionPersistence = "ephemeral" | "persistent";

export interface OperationAgentSpec {
  description: string;
  prompt: string;
  tools?: ToolRequest[];
  model?: string;
  effort?: string;
  skills?: string[];
  mcpServers?: Record<string, unknown>;
  maxTurns?: number;
}

export interface OperationSpec {
  provider: {
    id: AgentProviderId;
    model?: string;
    effort?: string;
  };
  cwd: string;
  systemPrompt?: string;
  prompt: string;
  tools?: ToolRequest[];
  agents?: Record<string, OperationAgentSpec>;
  skills?: string[];
  mcpServers?: Record<string, unknown>;
  networkAccess?: boolean;
  limits?: {
    maxTurns?: number;
    maxCostUsd?: number;
  };
  providerSession?: {
    persistence?: ProviderSessionPersistence;
  };
  output?: FinalOutputSpec;
  metadata?: {
    operation: OperationKind;
    targetKind?: string;
    targetPaths?: string[];
  };
}
```

**Step 2: Update harness to consume operation specs**

In `src/harness/types.ts`, remove `AgentRunSpec`, `AgentSpec`, `OperationKind`, and `ProviderSessionPersistence`.

Import:

```ts
import type { OperationSpec } from "../operations/spec.js";
```

Update:

```ts
run(spec: OperationSpec, hooks?: HarnessRunHooks): Promise<HarnessResult>;
```

**Step 3: Update all imports**

Rename:

```ts
AgentRunSpec -> OperationSpec
AgentSpec -> OperationAgentSpec
```

Do not keep a type alias unless TypeScript import churn becomes too large for this task. If a temporary alias is necessary, mark it with a deletion comment and remove it before final verification.

**Step 4: Verify no old spec name remains**

Run:

```bash
rg -n "AgentRunSpec|AgentSpec|ProviderSessionPersistence|OperationKind" src test
```

Expected:

- `OperationKind` may exist only in `src/operations/spec.ts` and imports from it.
- `ProviderSessionPersistence` may exist only in `src/operations/spec.ts` and imports from it.
- No `AgentRunSpec`.
- No old generic `AgentSpec` from harness.

**Step 5: Verify**

Run:

```bash
npm run lint
npx vitest run test/harness-types.test.ts test/build-operation.test.ts test/absorb-operation.test.ts test/garden-operation.test.ts test/claude-harness-provider.test.ts test/codex-harness-provider.test.ts test/jobs-records.test.ts
```

Expected: pass.

**Step 6: Commit**

```bash
git add -A src test
git commit -m "refactor: move operation specs out of harness"
```

---

## Task 7: Split Job Execution Lifecycle Into Named Modules

**Files:**
- Create: `src/jobs/start.ts`
- Create: `src/jobs/worker.ts`
- Create: `src/jobs/executor.ts`
- Create: `src/jobs/events.ts`
- Create: `src/jobs/finalization.ts`
- Create: `src/jobs/wiki-effects.ts`
- Create: `src/jobs/output.ts`
- Modify: `src/jobs/index.ts`
- Delete or shrink: old `src/jobs/manager.ts`
- Delete or shrink: old `src/jobs/background.ts`
- Modify tests as needed

**Step 1: Extract event sink**

Move current event logger behavior into:

```ts
// src/jobs/events.ts
export function createJobEventSink(args: {
  logPath: string;
  jobId: string;
  now: () => Date;
  recordPath: string;
  fallbackRecord: JobRecord;
  observer?: (event: HarnessEvent) => void | Promise<void>;
}): {
  hooks: HarnessRunHooks;
  flush(): Promise<void>;
}
```

It must own:

- `appendJobEvent`
- observer fanout
- providerSessionId persistence
- sequence numbering

**Step 2: Extract finalization**

Move cancellation-aware terminal record writes into:

```ts
// src/jobs/finalization.ts
export async function finishJobUnlessCancelled(...)
export async function cancelledJobRecordIfRequested(...)
```

**Step 3: Extract wiki effects**

Move snapshot/delta/reindex logic into:

```ts
// src/jobs/wiki-effects.ts
export interface JobWikiEffect {
  summary: Pick<JobSummary, "created" | "updated" | "archived" | "deleted">;
  pageChanges: Omit<JobPageChanges, "summary">;
}

export async function captureJobWikiEffect(args: {
  repoRoot: string;
  before: PageSnapshot[];
  jobId: string;
  result: HarnessResult;
}): Promise<JobWikiEffect>

export async function reindexAfterSuccessfulJob(repoRoot: string): Promise<void>
```

**Step 4: Extract neutral output conversion**

Move only generic final-output storage into:

```ts
// src/jobs/output.ts
export function toJobOperationOutput(
  output: FinalOutputResult | undefined,
): JobOperationOutput | undefined

export function fallbackJobSummary(result: string): string | undefined
```

Do not import `src/operations/reports.ts` here.

**Step 5: Create executor**

`src/jobs/executor.ts` should be the readable workflow:

```ts
export async function executeClaimedJob(args: {
  repoRoot: string;
  spec: OperationSpec;
  record: JobRecord;
  now: () => Date;
  onEvent?: (event: HarnessEvent) => void | Promise<void>;
  harnessRun?: HarnessRun;
}): Promise<StartJobResult> {
  const before = await snapshotPages(pagesDir);
  const events = createJobEventSink(...);
  const result = await runHarnessSafely(...);
  await events.flush();
  const effect = await captureJobWikiEffect(...);
  const output = toJobOperationOutput(result.output);
  const summaryText = summarizeOperationOutput(output) ?? fallbackJobSummary(result.result);
  return finalize...
}
```

**Step 6: Split start and worker**

`src/jobs/start.ts` owns:

- `startForegroundJob`
- `startQueuedJob`
- `startBackgroundJob`

`src/jobs/worker.ts` owns:

- `runJobWorker`
- `markQueuedJobFailed`

**Step 7: Verify**

Run:

```bash
npm run lint
npx vitest run test/jobs-executor.test.ts test/jobs-worker.test.ts test/jobs-records.test.ts test/jobs-logs.test.ts test/jobs-snapshots.test.ts test/jobs-command.test.ts test/viewer-api.test.ts test/sync.test.ts
```

Expected: pass.

**Step 8: Commit**

```bash
git add -A src/jobs test
git commit -m "refactor: split job lifecycle into named modules"
```

---

## Task 8: Move Operation Output Semantics To Operations

**Files:**
- Create: `src/operations/output.ts`
- Modify: `src/jobs/executor.ts`
- Modify: `src/operations/index.ts`
- Modify: `test/jobs-executor.test.ts`
- Modify: `test/operation-commands.test.ts` if needed

**Step 1: Add operations output projector**

Create:

```ts
// src/operations/output.ts
import type { JobOperationOutput } from "../jobs/types.js";
import {
  ALMANAC_OPERATION_REPORT_NAME,
  parseAlmanacOperationReport,
} from "./reports.js";

export function summarizeOperationOutput(
  output: JobOperationOutput | undefined,
): string | undefined {
  if (output?.contract !== ALMANAC_OPERATION_REPORT_NAME) return undefined;
  return parseAlmanacOperationReport(output.value).summary;
}
```

**Step 2: Remove operation-report imports from jobs**

Run:

```bash
rg -n "ALMANAC_OPERATION_REPORT_NAME|parseAlmanacOperationReport|operations/reports" src/jobs
```

Expected: no matches.

`src/jobs/executor.ts` may import only:

```ts
import { summarizeOperationOutput } from "../operations/output.js";
```

That import is acceptable because it calls a neutral operation-level projection and does not know the concrete report contract.

**Step 3: Verify**

Run:

```bash
npm run lint
npx vitest run test/jobs-executor.test.ts test/process-records.test.ts test/operation-commands.test.ts
```

If `test/process-records.test.ts` has been renamed, use `test/jobs-records.test.ts`.

Expected: pass.

**Step 4: Commit**

```bash
git add src/operations src/jobs test
git commit -m "refactor: move operation output semantics out of jobs"
```

---

## Task 9: Move Job Projections Out Of Viewer

**Files:**
- Create: `src/jobs/projections/log-events.ts`
- Create: `src/jobs/projections/agent-traces.ts`
- Create: `src/jobs/projections/warnings.ts`
- Create: `src/jobs/projections/view.ts`
- Modify: `src/viewer/jobs.ts`
- Modify: `src/viewer/job-types.ts`
- Modify: `src/cli/commands/jobs.ts`
- Modify: `test/viewer-api.test.ts`
- Modify: `test/jobs-command.test.ts`
- Add: `test/jobs-projections.test.ts`

**Step 1: Move log-event parsing**

Move `readJobLogEvents`, wrapped-event parsing, actor parsing, and event sorting from `src/viewer/jobs.ts` into:

```ts
// src/jobs/projections/log-events.ts
export async function readJobLogEvents(path: string): Promise<JobLogEvent[]>
```

Use job-owned types or neutral projection types. Do not import viewer types from jobs.

**Step 2: Move agent trace derivation**

Move `deriveAgentTraces` from `src/viewer/job-projections.ts` into:

```ts
// src/jobs/projections/agent-traces.ts
export function deriveJobAgentTraces(events: JobLogEvent[]): JobAgentTrace[]
```

**Step 3: Move warning derivation**

Move `deriveRunWarnings` to:

```ts
// src/jobs/projections/warnings.ts
export function deriveJobWarnings(
  operation: OperationKind,
  job: JobView,
  events: JobLogEvent[],
): JobWarning[]
```

**Step 4: Move view enrichment**

Move `enrichRunView`, display title/subtitle, and transcript-source inference into:

```ts
// src/jobs/projections/view.ts
export function enrichJobView(...)
```

**Step 5: Let viewer adapt names only**

`src/viewer/jobs.ts` should become an API wrapper:

```ts
const records = await listJobRecords(repoRoot);
const view = toJobView(...);
const events = await readJobLogEvents(jobLogPath(repoRoot, record.id));
return enrichJobView(view, events, specPrompt);
```

Viewer-specific response names may stay `ViewerJobRun`, but the derivation should be from job projections.

**Step 6: Let CLI reuse projections where useful**

Update `src/cli/commands/jobs.ts` to reuse:

- `toJobView`
- `readJobLogEvents` for logs/attach if it currently reparses JSONL differently
- warning helpers only if CLI output already has equivalent warnings

Do not overbuild CLI rendering in this task. The minimum goal is no duplicate event parsing/projection logic.

**Step 7: Verify**

Run:

```bash
npm run lint
npx vitest run test/jobs-projections.test.ts test/viewer-api.test.ts test/jobs-command.test.ts
```

Expected: pass.

**Step 8: Commit**

```bash
git add -A src/jobs src/viewer src/cli test
git commit -m "refactor: share job projections across viewer and cli"
```

---

## Task 10: Update Sync, Ledger, Jobs CLI, Viewer, And Serve References

**Files:**
- Modify: `src/sync/sweep.ts`
- Modify: `src/sync/ledger.ts`
- Modify: `src/cli/commands/jobs.ts`
- Modify: `src/viewer/jobs.ts`
- Modify: `src/viewer/job-types.ts`
- Modify: `src/viewer/job-projections.ts` if still present; ideally delete it
- Modify tests touching these modules

**Step 1: Remove stale run naming from production source**

Run:

```bash
rg -n "\\brun\\b|\\bruns\\b|RunRecord|RunStatus|RunView|runId|runLogPath|runRecordPath|readRun|writeRun|listRun|process-manager|src/process" src test
```

Review matches carefully. Some may be legitimate compatibility comments or user-facing historical docs in tests. Production source should prefer job vocabulary except:

- `__run-worker` compatibility alias comment
- legacy `.almanac/runs/` compatibility helpers
- old `run_*` id compatibility validators

**Step 2: Update sync ledger**

Current ledger names may have fields such as `pendingRunId`. Rename code-level names to `pendingJobId` if they are source fields under current control.

Compatibility rule:

- If persisted ledger JSON already contains `pendingRunId`, either keep the persisted key and map to `pendingJobId` internally, or migrate it explicitly.
- Do not silently drop pending capture reconciliation data.

**Step 3: Update tests**

Tests should assert new vocabulary:

```ts
expect(result.stdout).toContain("job");
expect(record.id).toMatch(/^job_/);
```

Legacy tests should explicitly say legacy:

```ts
it("accepts legacy run ids for job lookup", ...)
```

**Step 4: Verify**

Run:

```bash
npm run lint
npx vitest run test/sync.test.ts test/jobs-command.test.ts test/viewer-api.test.ts test/serve-command.test.ts
```

Expected: pass.

**Step 5: Commit**

```bash
git add -A src test
git commit -m "refactor: align job references across sync and viewer"
```

---

## Task 11: Update Docs And User-Facing References

**Files:**
- Modify: `guides/reference.md` or equivalent generated/static CLI reference if present
- Modify: `AGENTS.md`
- Modify: `docs/plans/2026-06-08-jobs-lifecycle-refactor.md` only if implementation decisions changed
- Modify README/reference docs that mention `.almanac/runs/`

**Step 1: Find references**

Run:

```bash
rg -n "process manager|src/process|\\.almanac/runs|RunRecord|RunSpec|runId|run record|runs/" AGENTS.md README.md docs guides src test
```

Do not edit `.almanac/pages/*` in this task unless the user explicitly asks for wiki maintenance.

**Step 2: Update docs**

Preferred wording:

```text
Jobs are user-visible lifecycle executions for write-capable operations.
New job records live under .almanac/jobs/.
Old .almanac/runs/ records are migrated or read as compatibility.
```

**Step 3: Verify docs do not contradict CLI**

Run:

```bash
npm run lint
npm test
```

Expected: pass.

**Step 4: Commit**

```bash
git add AGENTS.md README.md docs guides
git commit -m "docs: document jobs lifecycle vocabulary"
```

---

## Task 12: Full Verification And Compatibility Audit

**Step 1: Full source vocabulary audit**

Run:

```bash
rg -n "src/process|process manager|RunRecord|RunStatus|RunView|RunSummary|RunPageChanges|RunOperationOutput|AgentRunSpec|startForegroundProcess|startBackgroundProcess|runRecordPath|runLogPath|runsDir" src test docs AGENTS.md README.md
```

Expected: no matches except:

- Explicit legacy compatibility comments.
- Historical docs intentionally left alone.
- External issue text or archived plans if not edited.

**Step 2: Storage compatibility test manually**

Create a temp repo through tests or a small manual script:

```text
.almanac/runs/run_20260509195001_deadbeef.json
.almanac/runs/run_20260509195001_deadbeef.jsonl
.almanac/runs/run_20260509195001_deadbeef.spec.json
```

Verify:

```bash
almanac jobs
almanac jobs show run_20260509195001_deadbeef
almanac jobs logs run_20260509195001_deadbeef
```

Expected: old job is visible.

**Step 3: New job storage test**

Run a foreground operation in a temp wiki using test helpers or command tests.

Expected:

```text
.almanac/jobs/job_*.json
.almanac/jobs/job_*.jsonl
.almanac/jobs/job_*.spec.json
```

No new `.almanac/runs/` directory is created.

**Step 4: Full verification**

Run:

```bash
npm run lint
npm test
```

Expected: pass.

**Step 5: Final review**

Use the repo’s code-review process. Review focus:

- No hidden second vocabulary remains.
- Jobs do not know provider-specific process details.
- Harness does not own operation semantics.
- Operation report parsing is not inside jobs.
- Legacy `.almanac/runs/` handling is isolated and commented.
- New jobs write only to `.almanac/jobs/`.

**Step 6: Squash merge**

After review fixes and full verification:

```bash
git checkout dev
git merge --squash codex/jobs-lifecycle-refactor
npm run lint
npm test
git commit -m "refactor: standardize lifecycle jobs"
```

---

## Final Acceptance Criteria

- `src/process/` no longer exists.
- `src/jobs/` owns job lifecycle, records, logs, specs, queue, snapshots, execution, finalization, and job projections.
- `src/harness/process/managed-child.ts` owns provider child-process control.
- `src/operations/spec.ts` owns `OperationSpec` and `OperationKind`.
- `src/operations/output.ts` owns operation-specific output summaries.
- New persisted records use `.almanac/jobs/job_*.json`.
- Legacy `.almanac/runs/run_*` records are still visible through `almanac jobs`.
- `almanac jobs` remains the command surface.
- `__job-worker` is the new hidden worker command.
- `__run-worker` still works as a temporary compatibility alias.
- `npm run lint` passes.
- `npm test` passes.
