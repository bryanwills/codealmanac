import { homedir } from "node:os";
import {
  readProgramArgumentAfter,
  removeLaunchdJob,
  type ExecFn,
} from "../../platform/automation/launchd.js";
import { detectLegacyCaptureSweepAutomation } from "../../platform/automation/legacy-capture.js";
import {
  DEFAULT_SYNC_QUIET,
  defaultCapturePlistPath,
  defaultSyncPlistPath,
} from "../../platform/automation/tasks.js";
import { runAutomationInstall } from "./automation.js";
import { renderOutcome } from "../outcome.js";

export interface MigrateCommandOutput {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export interface MigrateAutomationOptions {
  json?: boolean;
  homeDir?: string;
  legacyPlistPath?: string;
  syncPlistPath?: string;
  exec?: ExecFn;
}

export async function runMigrateAutomation(
  options: MigrateAutomationOptions = {},
): Promise<MigrateCommandOutput> {
  const home = options.homeDir ?? homedir();
  const legacyPlistPath = options.legacyPlistPath ?? defaultCapturePlistPath(home);
  const syncPlistPath = options.syncPlistPath ?? defaultSyncPlistPath(home);
  const legacy = await detectLegacyCaptureSweepAutomation({
    homeDir: home,
    plistPath: legacyPlistPath,
  });
  if (legacy === null) {
    return renderOutcome(
      {
        type: "noop",
        message: "automation already current",
        data: { legacyPlistPath, syncPlistPath },
      },
      { json: options.json },
    );
  }

  const quiet = readProgramArgumentAfter(legacy.contents, "--quiet") ?? DEFAULT_SYNC_QUIET;
  const every = legacy.intervalSeconds === null
    ? undefined
    : `${legacy.intervalSeconds}s`;
  const installed = await runAutomationInstall({
    tasks: ["sync"],
    every,
    quiet,
    plistPath: syncPlistPath,
    exec: options.exec,
  });
  if (installed.exitCode !== 0) return installed;
  await removeLaunchdJob(legacyPlistPath, options.exec);
  return renderOutcome(
    {
      type: "success",
      message: "migrated automation to sync",
      data: {
        legacyPlistPath,
        syncPlistPath,
        quiet,
        intervalSeconds: legacy.intervalSeconds,
      },
    },
    {
      json: options.json,
      stdout:
        "almanac: migrated automation to sync\n" +
        `  sync plist: ${syncPlistPath}\n` +
        `  removed legacy plist: ${legacyPlistPath}\n`,
    },
  );
}
