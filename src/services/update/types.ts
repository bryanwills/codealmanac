import type { spawn } from "node:child_process";

import type { checkForUpdate } from "../../platform/update/check.js";
import type { InstallLatestPackageResult } from "../../platform/update/install.js";

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

export type UpdateWorkflowResult =
  | { status: "notifier-updated"; enabled: boolean }
  | { status: "no-pending-dismiss" }
  | { status: "dismiss-already-current"; installed: string }
  | { status: "already-dismissed"; latest: string }
  | { status: "dismissed"; latest: string }
  | { status: "registry-unreachable"; installed: string; action: "check" | "install" }
  | { status: "registry-missing-latest"; installed: string }
  | { status: "update-available"; installed: string; latest: string; dismissed: boolean }
  | { status: "up-to-date"; installed: string }
  | { status: "dismissed-install-skipped"; latest: string }
  | { status: "install-in-progress" }
  | { status: "install-result"; result: InstallLatestPackageResult };
