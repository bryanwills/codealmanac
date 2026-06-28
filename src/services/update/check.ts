import {
  readState,
  writeState,
  type UpdateState,
} from "../../stores/update/index.js";
import type {
  UpdateCheckRequest,
  UpdateCheckResult,
  UpdateLatestVersionFn,
} from "../../shared/update-runtime.js";

/**
 * Update check/cache workflow shared by the manual update command and the
 * detached update-check worker.
 *
 * Contract:
 *   - Reads `~/.almanac/update-state.json` if present.
 *   - If the last check is older than `cacheSeconds` (default 24h), asks the
 *     injected runtime for the latest package version and writes a new state.
 *   - All errors are swallowed; the returned state is always a usable
 *     snapshot, possibly the old one when the runtime fetch failed.
 */

export interface CheckForUpdateOptions extends UpdateCheckRequest {
  fetchLatestVersion: UpdateLatestVersionFn;
}

const DEFAULT_CACHE_SECONDS = 24 * 60 * 60;
const DEFAULT_TIMEOUT_MS = 3000;

export async function checkForUpdate(
  opts: CheckForUpdateOptions,
): Promise<UpdateCheckResult> {
  const now = opts.now ?? (() => Math.floor(Date.now() / 1000));
  const cacheSeconds = opts.cacheSeconds ?? DEFAULT_CACHE_SECONDS;
  const timeoutMs = opts.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const installed = opts.installedVersion ?? "";

  const state = await readState(opts.statePath);

  // Cache gate. Skip the registry call when the previous check is
  // fresh enough, unless `force: true` (used by `update --check` so
  // the user can see real-time status without waiting out the window).
  if (
    !opts.force &&
    state.last_check_at > 0 &&
    now() - state.last_check_at < cacheSeconds
  ) {
    return { state, fetched: false, fetchFailed: false };
  }

  const latestVersion = await opts.fetchLatestVersion({ timeoutMs });
  const failed = !latestVersion.ok;
  const latest = latestVersion.ok ? latestVersion.latest : null;

  if (failed || latest === null) {
    // Record the failure but DON'T clobber the previous latest_version —
    // an offline check shouldn't make us forget that 0.1.6 is out.
    const next: UpdateState = {
      ...state,
      // We still bump last_check_at on a failed attempt; without this,
      // every subsequent command would re-try the registry. A one-shot
      // retry on the next invocation is enough; sustained failure gets
      // retried on the 24h cadence like a success.
      last_check_at: now(),
      installed_version: installed,
      last_fetch_failed_at: now(),
    };
    try {
      await writeState(next, opts.statePath);
    } catch {
      // Even the state write failed (permissions, disk full). Return
      // whatever we have — the CLI doesn't care.
    }
    return { state: next, fetched: true, fetchFailed: true };
  }

  const next: UpdateState = {
    last_check_at: now(),
    installed_version: installed,
    latest_version: latest,
    dismissed_versions: state.dismissed_versions,
    // Clear the failure marker on success.
    last_fetch_failed_at: undefined,
  };
  try {
    await writeState(next, opts.statePath);
  } catch {
    // Silent — same rationale as above.
  }
  return { state: next, fetched: true, fetchFailed: false };
}
