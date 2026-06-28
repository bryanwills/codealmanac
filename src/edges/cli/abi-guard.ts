import { createRequire } from "node:module";
import { homedir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  readInstallRuntimeSync,
  sameExecutablePath,
} from "../../platform/install/launcher-runtime.js";

/**
 * Check whether the `better-sqlite3` native binding is compatible with
 * the currently-running Node version. Called once at startup, before any
 * commander setup or wiki code runs, so users see a clear, actionable
 * error instead of a cryptic `NODE_MODULE_VERSION` stack trace deep inside
 * the indexer.
 */
export function checkSqliteAbi(): string | null {
  const req = createRequire(import.meta.url);
  try {
    const Database = req("better-sqlite3") as typeof import("better-sqlite3");
    const db = new Database(":memory:");
    db.close();
    return null;
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    const firstLine = msg.split("\n")[0] ?? msg;
    const versionMatch = firstLine.match(/Expected (\d+), got (\d+)/);
    const detail = versionMatch
      ? ` (built for Node ABI ${versionMatch[1]}, running ABI ${versionMatch[2]})`
      : `: ${firstLine}`;

    const installDir = detectInstallDir();
    const launcherHint = renderLauncherHint();

    return (
      `better-sqlite3 native binding failed${detail}.\n` +
      `  Fix: cd "${installDir}" && npm rebuild better-sqlite3\n` +
      `  Or switch back to the Node version it was compiled for: nvm use <version>` +
      launcherHint
    );
  }
}

export function shouldCheckSqliteAbi(argv: string[]): boolean {
  const invoked = process.env.CODEALMANAC_INVOKED_AS ??
    argv[1]?.split(/[\\/]/).pop() ??
    "almanac";
  const args = argv.slice(2);

  if (args.includes("--internal-check-updates")) return false;
  if (args.length === 1 && (args[0] === "--version" || args[0] === "-v")) {
    return false;
  }

  if (invoked === "almanac" || invoked === "codealmanac") {
    if (args.length === 0) return false;
    if (
      args.every((arg) =>
        arg === "--yes" ||
        arg === "-y" ||
        arg === "--skip-automation" ||
        arg === "--skip-guides"
      )
    ) {
      return false;
    }
  }

  const sqliteFreeCommands = new Set([
    "setup",
    "automation",
    "uninstall",
    "update",
    "doctor",
  ]);
  const firstCommand = args.find((arg) => !arg.startsWith("-"));
  return firstCommand === undefined || !sqliteFreeCommands.has(firstCommand);
}

function renderLauncherHint(): string {
  const runtime = readInstallRuntimeSync(
    path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../.."),
  );
  if (runtime === null || sameExecutablePath(runtime.nodePath, process.execPath)) {
    return "";
  }

  return (
    `\n\nRunning Node:\n` +
    `  ${process.execPath} ${process.version}\n\n` +
    `Install-time Node:\n` +
    `  ${runtime.nodePath} ${runtime.nodeVersion}` +
    `${runtime.nodeAbi !== null ? ` (ABI ${runtime.nodeAbi})` : ""}\n\n` +
    `Repair:\n` +
    `  run the installed almanac launcher, or reinstall:\n` +
    `  npm install -g codealmanac@latest`
  );
}

function detectInstallDir(): string {
  try {
    const here = fileURLToPath(import.meta.url);
    const req = createRequire(import.meta.url);
    let dir = path.dirname(here);
    for (let i = 0; i < 6; i += 1) {
      const pkgPath = path.join(dir, "package.json");
      try {
        const raw = req("fs").readFileSync(pkgPath, "utf-8") as string;
        const pkg = JSON.parse(raw) as { name?: unknown };
        if (pkg.name === "codealmanac") return dir;
      } catch {
        // Keep walking. Source and packaged layouts differ.
      }
      const parent = path.dirname(dir);
      if (parent === dir) break;
      dir = parent;
    }
  } catch {
    // Fall through to the generic global-install hint.
  }

  return path.join(
    homedir(),
    ".nvm/versions/node",
    process.version,
    "lib/node_modules/codealmanac",
  );
}
