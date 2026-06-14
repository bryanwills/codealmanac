import type { HarnessResult } from "../harness/events.js";
import type { FinalOutputResult } from "../harness/final-output.js";
import { describeOperationOutput } from "../operations/output.js";
import { runIndexer } from "../wiki/indexer/index.js";
import { diffPageSnapshots, snapshotWikiPages } from "./snapshots.js";
import type {
  JobOperationOutput,
  JobPageChanges,
  JobSummary,
} from "./types.js";
import type { PageSnapshot } from "./snapshots.js";

export interface JobWikiSnapshot {
  repoRoot: string;
  before: PageSnapshot;
}

export interface JobWikiEffects {
  summary: JobSummary;
  pageChanges: JobPageChanges;
  operationOutput?: JobOperationOutput;
}

export async function snapshotJobWiki(repoRoot: string): Promise<JobWikiSnapshot> {
  return {
    repoRoot,
    before: await snapshotWikiPages(repoRoot),
  };
}

export async function collectJobWikiEffects(args: {
  snapshot: JobWikiSnapshot;
  jobId: string;
  result: HarnessResult;
}): Promise<JobWikiEffects> {
  const after = await snapshotWikiPages(args.snapshot.repoRoot);
  const delta = diffPageSnapshots(args.snapshot.before, after);
  const summary: JobSummary = {
    created: delta.created.length,
    updated: delta.updated.length,
    deleted: delta.deleted.length,
    costUsd: args.result.costUsd,
    turns: args.result.turns,
    usage: args.result.usage,
  };
  const operationOutput = jobOperationOutput(args.result.output);
  const resultDescription =
    describeOperationOutput(operationOutput) ??
    harnessResultDescription(args.result.result);
  const pageChanges: JobPageChanges = {
    version: 1,
    jobId: args.jobId,
    created: delta.created,
    updated: delta.updated,
    deleted: delta.deleted,
    ...(resultDescription !== undefined ? { description: resultDescription } : {}),
  };
  return { summary, pageChanges, operationOutput };
}

export async function reindexSuccessfulJob(repoRoot: string): Promise<void> {
  await runIndexer({ repoRoot });
}

function harnessResultDescription(result: string): string | undefined {
  for (const rawLine of result.split(/\r?\n/)) {
    const line = rawLine.replace(/^#+\s*/, "").trim();
    if (line.length === 0 || line === "---") continue;
    return line.length > 500 ? `${line.slice(0, 497)}...` : line;
  }
  return undefined;
}

function jobOperationOutput(
  output: FinalOutputResult | undefined,
): JobOperationOutput | undefined {
  if (output?.kind !== "json_schema") return undefined;
  return {
    version: 1,
    contract: output.name,
    value: output.value,
  };
}
