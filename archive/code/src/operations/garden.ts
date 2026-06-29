import type { OperationSpec } from "./spec.js";
import { findNearestAlmanacDir } from "../paths.js";
import { MissingWikiError } from "./errors.js";
import { canonicalWikiDir, reviewYamlPath } from "../wiki/locations.js";
import type {
  OperationProviderSelection,
  OperationRunResult,
  StartBackgroundJob,
  StartForegroundJob,
} from "./types.js";
import { createOperationRunSpec, runOperationProcess } from "./run.js";

export interface GardenOperationOptions {
  cwd: string;
  provider?: OperationProviderSelection;
  background?: boolean;
  context?: string;
  jobId?: string;
  onEvent?: (event: import("../harness/events.js").HarnessEvent) => void | Promise<void>;
  startForeground?: StartForegroundJob;
  startBackground?: StartBackgroundJob;
}

export async function createGardenRunSpec(args: {
  repoRoot: string;
  provider?: OperationProviderSelection;
  context?: string;
}): Promise<OperationSpec> {
  return createOperationRunSpec({
    operation: "garden",
    promptName: "operations/garden",
    provider: args.provider,
    repoRoot: args.repoRoot,
    context: args.context,
    targetKind: "wiki",
    targetPaths: [canonicalWikiDir(args.repoRoot), reviewYamlPath(args.repoRoot)],
  });
}

export async function runGardenOperation(
  options: GardenOperationOptions,
): Promise<OperationRunResult> {
  const repoRoot = findNearestAlmanacDir(options.cwd);
  if (repoRoot === null) throw new MissingWikiError();
  const spec = await createGardenRunSpec({
    repoRoot,
    provider: options.provider,
    context: options.context,
  });

  return runOperationProcess({
    repoRoot,
    spec,
    background: options.background !== false,
    jobId: options.jobId,
    onEvent: options.onEvent,
    startForeground: options.startForeground,
    startBackground: options.startBackground,
  });
}
