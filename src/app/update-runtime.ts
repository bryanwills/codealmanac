import { fetchLatestVersion } from "../platform/update/check.js";
import {
  installLatestPackage,
  type InstallLatestPackageResult,
} from "../platform/update/install.js";
import { readInstalledVersion } from "../platform/update/version.js";
import { checkForUpdate } from "../services/update/check.js";
import type {
  UpdateInstallResult,
  UpdateRuntime,
} from "../shared/update-runtime.js";

export function createUpdateRuntime(): UpdateRuntime {
  return {
    readInstalledVersion,
    checkForUpdate: (request) =>
      checkForUpdate({
        ...request,
        installedVersion: request?.installedVersion ?? readInstalledVersion(),
        fetchLatestVersion,
      }),
    async installLatestPackage() {
      return updateInstallResultFromPlatform(await installLatestPackage());
    },
  };
}

export async function runInternalUpdateCheck(): Promise<void> {
  try {
    const runtime = createUpdateRuntime();
    await runtime.checkForUpdate({
      installedVersion: runtime.readInstalledVersion(),
    });
  } catch {
    // Nothing from the worker should escape into the foreground command.
  }
}

function updateInstallResultFromPlatform(
  result: InstallLatestPackageResult,
): UpdateInstallResult {
  return {
    output: result.stdout,
    errorOutput: result.stderr,
    code: result.exitCode,
  };
}
