import { existsSync } from "node:fs";
import { readdir } from "node:fs/promises";
import { join } from "node:path";

import type { OperationSpec } from "./spec.js";
import { initWiki } from "../init/scaffold.js";
import type {
  JobWorkerProgram,
  OperationProviderSelection,
  OperationRunResult,
  StartBackgroundJob,
  StartForegroundJob,
} from "./types.js";
import { OperationError } from "./errors.js";
import { createOperationRunSpec, runOperationProcess } from "./run.js";

export interface BuildOperationOptions {
  cwd: string;
  provider?: OperationProviderSelection;
  background?: boolean;
  context?: string;
  force?: boolean;
  jobId?: string;
  onEvent?: (event: import("../agent/runtime/events.js").AgentRuntimeEvent) => void | Promise<void>;
  startForeground?: StartForegroundJob;
  startBackground?: StartBackgroundJob;
  workerProgram: JobWorkerProgram;
  workerEnvironment: NodeJS.ProcessEnv;
  pid: number;
}

export async function createBuildRunSpec(args: {
  repoRoot: string;
  provider?: OperationProviderSelection;
  context?: string;
}): Promise<OperationSpec> {
  return createOperationRunSpec({
    operation: "build",
    promptName: "operations/build",
    provider: args.provider,
    repoRoot: args.repoRoot,
    context: args.context,
    targetKind: "repo",
    targetPaths: [args.repoRoot],
  });
}

export async function runBuildOperation(
  options: BuildOperationOptions,
): Promise<OperationRunResult> {
  const init = await initWiki({ cwd: options.cwd });
  const repoRoot = init.entry.path;
  const pageCount = await countWikiPages(repoRoot);
  if (pageCount > 0 && options.force !== true) {
    throw new OperationError(
      `.almanac/ already initialized with ${pageCount} page${pageCount === 1 ? "" : "s"}; pass --force to rebuild`,
      {
        outcome: "needs-action",
        fix: "run: almanac init --force",
        data: { pageCount },
      },
    );
  }
  const spec = await createBuildRunSpec({
    repoRoot,
    provider: options.provider,
    context: options.context,
  });

  return runOperationProcess({
    repoRoot,
    spec,
    background: options.background === true,
    jobId: options.jobId,
    onEvent: options.onEvent,
    startForeground: options.startForeground,
    startBackground: options.startBackground,
    workerProgram: options.workerProgram,
    workerEnvironment: options.workerEnvironment,
    pid: options.pid,
  });
}

async function countWikiPages(repoRoot: string): Promise<number> {
  const pagesDir = join(repoRoot, ".almanac", "pages");
  if (!existsSync(pagesDir)) return 0;
  const entries = await readdir(pagesDir);
  return entries.filter((entry) => entry.endsWith(".md")).length;
}
