import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { userInfo } from "node:os";
import path from "node:path";
import { promisify } from "node:util";

import {
  readLaunchdStartInterval,
  renderLaunchdPlist,
  type LaunchdPlistDefinition,
} from "./launchd-plist.js";

const execFileAsync = promisify(execFile);

const LAUNCHD_FALLBACK_PATHS = [
  "/usr/local/bin",
  "/opt/homebrew/bin",
  "/usr/bin",
  "/bin",
  "/usr/sbin",
  "/sbin",
];

export interface LaunchdJobDefinition extends LaunchdPlistDefinition {
  label: string;
  plistPath: string;
}

export type ExecFn = (
  file: string,
  args: string[],
) => Promise<{ stdout?: string; stderr?: string }>;

export interface LaunchdPlistStatus {
  installed: boolean;
  plistPath: string;
  contents: string | null;
  intervalSeconds: number | null;
}

export interface LaunchdJobStatus extends LaunchdPlistStatus {
  loaded: boolean;
}

export function launchdTarget(): string {
  return `gui/${userInfo().uid}`;
}

export function buildLaunchPath(home: string, envPath: string | undefined): string {
  const installPaths = (envPath ?? "")
    .split(":")
    .map((entry) => entry.trim())
    .filter(Boolean);
  const userPaths = [
    path.join(home, ".local", "bin"),
    path.join(home, ".bun", "bin"),
  ];
  return unique([...installPaths, ...userPaths, ...LAUNCHD_FALLBACK_PATHS])
    .join(":");
}

export async function ensureLaunchdDirs(jobs: LaunchdJobDefinition[]): Promise<void> {
  await Promise.all([
    ...jobs.map((job) => mkdir(path.dirname(job.plistPath), { recursive: true })),
    ...unique(
      jobs.flatMap((job) => [
        path.dirname(job.stdoutPath),
        path.dirname(job.stderrPath),
      ]),
    )
      .map((dir) => mkdir(dir, { recursive: true })),
  ]);
}

export async function writeLaunchdPlist(job: LaunchdJobDefinition): Promise<void> {
  await writeFile(job.plistPath, renderLaunchdPlist(job), "utf8");
}

export async function bootstrapLaunchdJob(
  plistPath: string,
  exec: ExecFn = defaultExec,
): Promise<void> {
  const target = launchdTarget();
  try {
    await exec("launchctl", ["bootout", target, plistPath]);
  } catch {
    // Not loaded yet is fine; bootstrap below is the authoritative install.
  }
  await exec("launchctl", ["bootstrap", target, plistPath]);
}

export async function removeLaunchdJob(
  plistPath: string,
  exec: ExecFn = defaultExec,
): Promise<boolean> {
  if (!existsSync(plistPath)) return false;
  try {
    await exec("launchctl", ["bootout", launchdTarget(), plistPath]);
  } catch {
    // Already unloaded is still a successful uninstall.
  }
  await rm(plistPath, { force: true });
  return true;
}

export async function readLaunchdPlistStatus(
  plistPath: string,
): Promise<LaunchdPlistStatus> {
  if (!existsSync(plistPath)) {
    return { installed: false, plistPath, contents: null, intervalSeconds: null };
  }
  const contents = await readFile(plistPath, "utf8");
  return {
    installed: true,
    plistPath,
    contents,
    intervalSeconds: readLaunchdStartInterval(contents),
  };
}

export async function readLaunchdJobStatus(args: {
  label: string;
  plistPath: string;
  exec?: ExecFn;
}): Promise<LaunchdJobStatus> {
  const plist = await readLaunchdPlistStatus(args.plistPath);
  return {
    ...plist,
    loaded: await isLaunchdJobLoaded(args.label, args.exec),
  };
}

async function isLaunchdJobLoaded(
  label: string,
  exec: ExecFn = defaultExec,
): Promise<boolean> {
  try {
    await exec("launchctl", ["print", `${launchdTarget()}/${label}`]);
    return true;
  } catch {
    return false;
  }
}

function unique(values: string[]): string[] {
  return [...new Set(values)];
}

async function defaultExec(
  file: string,
  args: string[],
): Promise<{ stdout?: string; stderr?: string }> {
  return await execFileAsync(file, args);
}
