import { spawn } from "node:child_process";
import type { ChildProcess } from "node:child_process";

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
  entrypoint: string;
  environment: NodeJS.ProcessEnv;
  spawnBackground?: SpawnBackgroundFn;
}): BackgroundChild {
  const spawnFn = args.spawnBackground ?? defaultSpawnBackground;
  return spawnFn({
    command: process.execPath,
    args: [args.entrypoint, "__job-worker"],
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
