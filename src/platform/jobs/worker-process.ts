import { spawn } from "node:child_process";
import type { ChildProcess } from "node:child_process";

import type { JobWorkerProgram } from "../../shared/worker-program.js";

export interface BackgroundChild {
  pid?: number;
  unref?: () => void;
}

export type SpawnBackgroundFn = (args: {
  command: string;
  args: string[];
  cwd: string;
  env: NodeJS.ProcessEnv;
}) => BackgroundChild;

export function startJobWorkerProcess(args: {
  repoRoot: string;
  workerProgram: JobWorkerProgram;
  environment: NodeJS.ProcessEnv;
  spawnBackground?: SpawnBackgroundFn;
}): BackgroundChild {
  const spawnFn = args.spawnBackground ?? defaultSpawnBackground;
  return spawnFn({
    command: args.workerProgram.command,
    args: [args.workerProgram.entrypoint, "__job-worker"],
    cwd: args.repoRoot,
    env: { ...args.environment },
  });
}

function defaultSpawnBackground(args: {
  command: string;
  args: string[];
  cwd: string;
  env: NodeJS.ProcessEnv;
}): ChildProcess {
  return spawn(args.command, args.args, {
    cwd: args.cwd,
    env: args.env,
    detached: true,
    stdio: "ignore",
  });
}
