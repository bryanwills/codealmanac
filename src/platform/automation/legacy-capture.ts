import {
  readLaunchdPlistStatus,
  type LaunchdPlistStatus,
} from "./launchd.js";
import { defaultCapturePlistPath } from "./paths.js";

export interface LegacyCaptureSweepAutomation {
  plistPath: string;
  contents: string;
  intervalSeconds: number | null;
}

export async function detectLegacyCaptureSweepAutomation(options: {
  homeDir: string;
  plistPath?: string;
}): Promise<LegacyCaptureSweepAutomation | null> {
  const plistPath = options.plistPath ?? defaultCapturePlistPath(options.homeDir);
  const status = await readLaunchdPlistStatus(plistPath);
  return legacyCaptureSweepFromStatus(status);
}

export function legacyCaptureSweepFromStatus(
  status: LaunchdPlistStatus,
): LegacyCaptureSweepAutomation | null {
  if (status.contents === null || !usesLegacyCaptureSweep(status.contents)) {
    return null;
  }
  return {
    plistPath: status.plistPath,
    contents: status.contents,
    intervalSeconds: status.intervalSeconds,
  };
}

export function usesLegacyCaptureSweep(contents: string): boolean {
  return /<string>capture<\/string>\s*<string>sweep<\/string>/.test(contents);
}
