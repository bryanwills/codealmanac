import {
  readConfig,
  writeConfig,
  type GlobalConfig,
} from "../../config/index.js";
import { checkForUpdate } from "../../platform/update/check.js";
import { installLatestPackage } from "../../platform/update/install.js";
import { acquireUpdateLock } from "../../platform/update/lock.js";
import { isNewer } from "../../platform/update/semver.js";
import { readState, writeState } from "../../platform/update/state.js";
import { readInstalledVersion } from "../../platform/update/version.js";
import type { UpdateOptions, UpdateResult } from "./types.js";

export async function runUpdateWorkflow(
  opts: UpdateOptions = {},
): Promise<UpdateResult> {
  if (opts.enableNotifier === true) {
    return await toggleNotifier(true, opts);
  }
  if (opts.disableNotifier === true) {
    return await toggleNotifier(false, opts);
  }
  if (opts.dismiss === true) {
    return await dismissLatest(opts);
  }
  if (opts.check === true) {
    return await forceCheck(opts);
  }
  return await installIfNeeded(opts);
}

async function dismissLatest(opts: UpdateOptions): Promise<UpdateResult> {
  const state = await readState(opts.statePath);
  if (state.latest_version.length === 0) {
    return {
      stdout:
        "almanac: no pending update to dismiss. " +
        "Run `almanac update --check` to query the registry.\n",
      stderr: "",
      exitCode: 0,
    };
  }

  const installed = opts.installedVersion ?? readInstalledVersion();
  if (!isNewer(state.latest_version, installed)) {
    return {
      stdout: `almanac: already on latest (${installed}); nothing to dismiss.\n`,
      stderr: "",
      exitCode: 0,
    };
  }

  if (state.dismissed_versions.includes(state.latest_version)) {
    return {
      stdout: `almanac: ${state.latest_version} already dismissed.\n`,
      stderr: "",
      exitCode: 0,
    };
  }

  const next = {
    ...state,
    dismissed_versions: [...state.dismissed_versions, state.latest_version],
  };
  await writeState(next, opts.statePath);
  return {
    stdout:
      `almanac: dismissed ${state.latest_version}. The nag banner ` +
      `will not show for this version.\n` +
      `Run \`almanac update\` to upgrade, or \`almanac config set update_notifier true\` to re-enable nags.\n`,
    stderr: "",
    exitCode: 0,
  };
}

async function forceCheck(opts: UpdateOptions): Promise<UpdateResult> {
  const installed = opts.installedVersion ?? readInstalledVersion();
  const checkFn = opts.checkFn ?? checkForUpdate;
  const result = await checkFn({
    installedVersion: installed,
    force: true,
    statePath: opts.statePath,
    now: opts.now,
  });

  if (result.fetchFailed) {
    return {
      stdout: "",
      stderr:
        `almanac: could not reach registry.npmjs.org (timeout or network error).\n` +
        `Installed: ${installed}. No cached latest available.\n`,
      exitCode: 1,
    };
  }

  const latest = result.state.latest_version;
  if (latest.length === 0) {
    return {
      stdout: `almanac: installed ${installed}; registry did not report a latest tag.\n`,
      stderr: "",
      exitCode: 0,
    };
  }

  if (isNewer(latest, installed)) {
    const dismissed = result.state.dismissed_versions.includes(latest)
      ? " (dismissed — banner suppressed; `almanac update` still installs)"
      : "";
    return {
      stdout:
        `Almanac ${latest} available (you're on ${installed})${dismissed}.\n` +
        `Run: almanac update\n`,
      stderr: "",
      exitCode: 0,
    };
  }

  return {
    stdout: `almanac: up to date (${installed}).\n`,
    stderr: "",
    exitCode: 0,
  };
}

async function toggleNotifier(
  enable: boolean,
  opts: UpdateOptions,
): Promise<UpdateResult> {
  const config = await readConfig(opts.configPath);
  const next: GlobalConfig = { ...config, update_notifier: enable };
  await writeConfig(next, opts.configPath);
  return {
    stdout: enable
      ? "almanac: update notifier enabled. " +
        "The pre-command banner will show when a new version is available.\n"
      : "almanac: update notifier disabled. " +
        "No more pre-command banners. Run `almanac update --check` to see status.\n",
    stderr: enable
      ? "almanac: warning: `almanac update --enable-notifier` is deprecated; use `almanac config set update_notifier true`.\n"
      : "almanac: warning: `almanac update --disable-notifier` is deprecated; use `almanac config set update_notifier false`.\n",
    exitCode: 0,
  };
}

async function installIfNeeded(opts: UpdateOptions): Promise<UpdateResult> {
  const installed = opts.installedVersion ?? readInstalledVersion();
  const checkFn = opts.checkFn ?? checkForUpdate;
  const result = await checkFn({
    installedVersion: installed,
    force: true,
    statePath: opts.statePath,
    now: opts.now,
  });

  if (result.fetchFailed) {
    return {
      stdout: "",
      stderr:
        `almanac: could not reach registry.npmjs.org (timeout or network error).\n` +
        `Installed: ${installed}. No install attempted.\n`,
      exitCode: 1,
    };
  }

  const latest = result.state.latest_version;
  if (latest.length === 0) {
    return {
      stdout: `almanac: installed ${installed}; registry did not report a latest tag.\n`,
      stderr: "",
      exitCode: 0,
    };
  }
  if (!isNewer(latest, installed)) {
    return {
      stdout: `almanac: up to date (${installed}).\n`,
      stderr: "",
      exitCode: 0,
    };
  }
  if (result.state.dismissed_versions.includes(latest)) {
    return {
      stdout:
        `almanac: ${latest} is available but dismissed; no install attempted.\n` +
        `Run \`almanac update --check\` to inspect update state.\n`,
      stderr: "",
      exitCode: 0,
    };
  }

  const lock = await acquireUpdateLock({
    path: opts.lockPath,
    now: opts.now,
    staleSeconds: opts.lockStaleSeconds,
  });
  if (lock === null) {
    return {
      stdout: "almanac: update already in progress; no install attempted.\n",
      stderr: "",
      exitCode: 0,
    };
  }

  try {
    const install = await installLatestPackage({
      spawnFn: opts.spawnFn,
    });
    if (install.exitCode !== 0) return install;
    await refreshInstalledState(opts, latest);
    return install;
  } finally {
    await lock.release();
  }
}

async function refreshInstalledState(
  opts: UpdateOptions,
  latest: string,
): Promise<void> {
  try {
    const state = await readState(opts.statePath);
    const now = opts.now ?? (() => Math.floor(Date.now() / 1000));
    await writeState(
      {
        last_check_at: now(),
        installed_version: latest,
        latest_version: latest,
        dismissed_versions: state.dismissed_versions,
      },
      opts.statePath,
    );
  } catch {
    // Non-fatal: the next invocation will refresh state.
  }
}
