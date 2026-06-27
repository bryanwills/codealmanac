import { formatDuration } from "../../shared/duration.js";
import { isNewerVersion } from "../../shared/version.js";
import type { Check, DoctorOptions } from "./types.js";

export async function gatherUpdateChecks(
  options: DoctorOptions,
  installedVersion: string,
): Promise<Check[]> {
  const checks: Check[] = [];
  const status = options.updateStatus;

  if (status.latestVersion.length === 0) {
    checks.push({
      status: "info",
      key: "update.status",
      message: `on ${installedVersion}; no update check has run yet`,
      fix: "run: almanac update --check",
    });
  } else if (isNewerVersion(status.latestVersion, installedVersion)) {
    const dismissed = status.dismissedVersions.includes(status.latestVersion)
      ? " (dismissed — run `almanac update` to install anyway)"
      : "";
    checks.push({
      status: "problem",
      key: "update.status",
      message:
        `${status.latestVersion} available (you're on ${installedVersion})${dismissed}`,
      fix: "run: almanac update",
    });
  } else {
    checks.push({
      status: "ok",
      key: "update.status",
      message: `on latest (${installedVersion})`,
    });
  }

  if (status.lastCheckAt > 0) {
    const now = (options.now?.() ?? new Date()).getTime();
    const ageMs = now - status.lastCheckAt * 1000;
    const failedSuffix =
      status.lastFetchFailedAt !== undefined &&
      status.lastFetchFailedAt === status.lastCheckAt
        ? " (last attempt failed — will retry next invocation)"
        : "";
    checks.push({
      status: "info",
      key: "update.last_check",
      message: `last checked: ${formatDuration(ageMs)} ago${failedSuffix}`,
    });
  } else {
    checks.push({
      status: "info",
      key: "update.last_check",
      message: "last checked: never",
    });
  }

  checks.push({
    status: "info",
    key: "update.notifier",
    message: `update notifier: ${status.notifierEnabled ? "enabled" : "disabled"}`,
    fix: status.notifierEnabled
      ? undefined
      : "run: almanac config set update_notifier true",
  });

  if (status.dismissedVersions.length > 0) {
    checks.push({
      status: "info",
      key: "update.dismissed",
      message: `dismissed versions: ${status.dismissedVersions.join(", ")}`,
    });
  }

  return checks;
}
