import fg from "fast-glob";

import type { OperationSpec } from "./spec.js";
import { initWiki } from "../init/scaffold.js";
import { wikiPageRoots } from "../wiki/locations.js";
import type {
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
  onEvent?: (event: import("../harness/events.js").HarnessEvent) => void | Promise<void>;
  startForeground?: StartForegroundJob;
  startBackground?: StartBackgroundJob;
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
      `wiki already initialized with ${pageCount} page${pageCount === 1 ? "" : "s"}; pass --force to rebuild`,
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
  });
}

async function countWikiPages(repoRoot: string): Promise<number> {
  const roots = wikiPageRoots(repoRoot);
  let count = 0;
  for (const root of roots) {
    const entries = await fg("**/*.md", {
      cwd: root.dir,
      absolute: false,
      onlyFiles: true,
      ignore:
        root.label === "docs/almanac"
          ? ["README.md", "_manual/**", "_meta/**"]
          : [],
    });
    count += entries.length;
  }
  return count;
}
