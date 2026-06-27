import type { spawn } from "node:child_process";

import type { checkForUpdate } from "../../platform/update/check.js";

export interface UpdateOptions {
  dismiss?: boolean;
  check?: boolean;
  enableNotifier?: boolean;
  disableNotifier?: boolean;

  statePath?: string;
  configPath?: string;
  installedVersion?: string;
  checkFn?: typeof checkForUpdate;
  spawnFn?: typeof spawn;
  now?: () => number;
  lockPath?: string;
  lockStaleSeconds?: number;
}

export interface UpdateResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}
