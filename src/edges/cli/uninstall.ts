import { createAutomationScheduler } from "../../app/automation-runtime.js";
import { createSetupInstructionRuntime } from "../../app/setup-runtime.js";
import {
  removeSetupImportLine,
  removeSetupManagedBlock,
  uninstallSetup,
} from "../../services/setup/index.js";
import {
  renderAutomationKept,
  renderGuidesKept,
  renderUninstallComplete,
  renderUninstallResult,
  renderUninstallStart,
} from "./uninstall-render.js";
import { chooseUninstallRemoval } from "./uninstall/confirmation.js";
import { resolveUninstallTargetDirs } from "./uninstall/targets.js";

type AutomationExecFn = (
  file: string,
  args: string[],
) => Promise<{ stdout?: string; stderr?: string }>;

/**
 * `almanac uninstall` — the reverse of `setup`.
 *
 * Idempotent and order-insensitive: each step is a no-op if that
 * artifact was never installed. We remove exactly the things setup added,
 * nothing else:
 *
 *   1. The `@~/.claude/almanac.md` line from `~/.claude/CLAUDE.md`.
 *      Other content stays untouched. If removing our line leaves the
 *      file empty, we delete the file so our fingerprint doesn't persist
 *      as zero bytes.
 *   2. The guide files `~/.claude/almanac.md` and
 *      `~/.claude/almanac-reference.md`. Legacy `codealmanac*.md` guide
 *      files are removed too.
 *   3. Managed global instruction entries for Codex, Cursor, Windsurf,
 *      and OpenCode.
 *   4. The scheduled sync/Garden launchd jobs and legacy hook files.
 *
 * Flags:
 *   --yes           skip confirmations; remove everything
 *   --keep-automation leave the scheduler alone
 *   --keep-guides   leave the guides + CLAUDE.md import alone
 *
 * Non-interactive (no TTY) → behaves as if `--yes` was passed. Same
 * contract as `setup`.
 */

export interface UninstallOptions {
  yes?: boolean;
  keepAutomation?: boolean;
  keepGuides?: boolean;
  homeDir: string;

  // ─── Injection points ────────────────────────────────────────────
  automationPlistPath?: string;
  gardenPlistPath?: string;
  automationExec?: AutomationExecFn;
  claudeDir?: string;
  codexDir?: string;
  cursorDir?: string;
  windsurfDir?: string;
  opencodeDir?: string;
  isTTY: boolean;
  stdin: NodeJS.ReadableStream;
  stdout: NodeJS.WritableStream;
  color?: boolean;
}

export interface UninstallResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export async function runUninstall(
  options: UninstallOptions,
): Promise<UninstallResult> {
  const out = options.stdout;
  const interactive = options.isTTY && options.yes !== true;
  const targetDirs = resolveUninstallTargetDirs(options);
  const renderOptions = { color: options.color };

  out.write(renderUninstallStart());

  // Scheduler removal.
  const removeAutomation = await chooseUninstallRemoval({
    keep: options.keepAutomation,
    interactive,
    input: options.stdin,
    out,
    question: "Remove scheduled sync and Garden automation?",
    renderOptions,
  });
  if (!removeAutomation) {
    out.write(renderAutomationKept(renderOptions));
  }

  // Guide + import removal.
  const removeGuides = await chooseUninstallRemoval({
    keep: options.keepGuides,
    interactive,
    input: options.stdin,
    out,
    question: "Remove agent instructions?",
    renderOptions,
  });
  if (!removeGuides) {
    out.write(renderGuidesKept(renderOptions));
  }

  const result = await uninstallSetup({
    removeAutomation,
    removeGuides,
    homeDir: options.homeDir,
    automationPlistPath: options.automationPlistPath,
    gardenPlistPath: options.gardenPlistPath,
    automationScheduler: createAutomationScheduler({
      exec: options.automationExec,
    }),
    instructionsRuntime: createSetupInstructionRuntime(),
    ...targetDirs,
  });

  out.write(renderUninstallResult(result, renderOptions));
  out.write(renderUninstallComplete(renderOptions));

  return { stdout: "", stderr: "", exitCode: 0 };
}

/**
 * Remove the import line from a CLAUDE.md body. Match is line-anchored
 * (trimmed equality) so we don't munge a line that happens to include
 * the token as part of a longer string. Returns the unchanged body (and
 * `changed: false`) if the line isn't present — this is what makes the
 * command safe to run repeatedly.
 */
export function removeImportLine(contents: string): {
  changed: boolean;
  body: string;
} {
  return removeSetupImportLine(contents);
}

export function removeManagedBlock(
  contents: string,
  start: string,
  end: string,
): { changed: boolean; body: string } {
  return removeSetupManagedBlock(contents, start, end);
}
