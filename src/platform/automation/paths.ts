import { homedir } from "node:os";
import path from "node:path";

const LEGACY_CAPTURE_SWEEP_LABEL = "com.codealmanac.capture-sweep";
const SYNC_LABEL = "com.codealmanac.sync";

export function launchAgentPlistPath(
  label: string,
  home: string = homedir(),
): string {
  return path.join(home, "Library", "LaunchAgents", `${label}.plist`);
}

export function automationLogPaths(args: {
  home: string;
  stdoutLogName: string;
  stderrLogName: string;
}): { stdoutPath: string; stderrPath: string } {
  const logsDir = path.join(args.home, ".almanac", "logs");
  return {
    stdoutPath: path.join(logsDir, args.stdoutLogName),
    stderrPath: path.join(logsDir, args.stderrLogName),
  };
}

export function defaultCapturePlistPath(home: string = homedir()): string {
  return launchAgentPlistPath(LEGACY_CAPTURE_SWEEP_LABEL, home);
}

export function defaultSyncPlistPath(home: string = homedir()): string {
  return launchAgentPlistPath(SYNC_LABEL, home);
}
