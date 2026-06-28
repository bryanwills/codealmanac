export {
  CODEX_INSTRUCTIONS_END,
  CODEX_INSTRUCTIONS_START,
  hasCodexInstructions,
} from "../../../services/setup/index.js";
import { readSetupWikiState } from "../../../services/wiki/setup-state.js";
export { IMPORT_LINE, hasImportLine } from "./guides.js";
import { printNextSteps } from "./next-steps.js";
import { isSetupInterrupted } from "./input.js";
import {
  blue,
  makeSetupTheme,
  printBadge,
  printBanner,
  stepDone,
} from "./output.js";
import { runSetupFlow } from "./setup-flow.js";
import type {
  SetupOptions,
  SetupResult,
} from "./types.js";

/**
 * `almanac setup` — the MCP-style branded TUI that runs when a user
 * invokes bare `almanac`, explicit `almanac setup`, or the compatibility
 * `codealmanac` npx bootstrap alias.
 *
 * Model: `mcp-ts/src/setup.ts` from openalmanac. Same ASCII banner + badge
 * + step-indicator style, same interactive + `--yes` + non-interactive
 * modes.
 *
 * Setup configures:
 *
 *   1. Global agent instructions for the selected tools.
 *   2. A durable global install when running from an ephemeral `npx` path.
 *   3. Scheduled Almanac CLI self-update by default.
 *   4. Optional self-managed local sync/Garden automation, only when the
 *      user opts into handling automations themselves or passes explicit
 *      automation flags.
 *   5. Optional auto-commit for local lifecycle runs, only behind the
 *      self-managed automation branch or explicit `--auto-commit`.
 *
 * Everything is idempotent — running setup again is safe. `--yes` or a
 * non-TTY stdin skips prompts and uses setup-plan defaults.
 */
export type {
  AutomationExecFn,
  SetupOptions,
  SetupResult,
} from "./types.js";

// Entry point.

export async function runSetup(
  options: SetupOptions,
): Promise<SetupResult> {
  const cwd = options.cwd;
  const out = options.stdout;
  const theme = makeSetupTheme(options.color !== false);
  const interactive = options.isTTY && options.yes !== true;

  // No-op fast path. When the caller explicitly skipped every install
  // step, rendering the full banner + step markers + "Setup complete"
  // box is actively misleading — nothing was actually set up. Emit a
  // single terse line and exit so the user gets honest feedback and
  // piped callers (CI, scripts) don't parse through nine lines of ANSI
  // to conclude nothing happened.
  if (
    options.skipAutomation === true &&
    options.skipGuides === true &&
    options.autoCommit === undefined
  ) {
    out.write(
      "almanac: nothing to install — use --help to see what setup does\n",
    );
    return { stdout: "", stderr: "", exitCode: 0 };
  }

  printBanner(out, theme);
  printBadge(out, theme);

  let nextStepsMode: "hosted" | "self-managed" = "hosted";
  try {
    const flow = await runSetupFlow({
      options,
      out,
      theme,
      interactive,
    });
    if (!flow.ok) return flow.result;
    nextStepsMode = flow.nextStepsMode;
  } catch (err: unknown) {
    if (isSetupInterrupted(err)) {
      return {
        stdout: "",
        stderr: "almanac: setup cancelled\n",
        exitCode: 130,
      };
    }
    throw err;
  }

  stepDone(out, theme, blue(theme, "Setup complete"));
  out.write("\n");

  // Detect whether the current working directory is inside a repo that
  // already has a wiki with pages. This fixes Bug #6 from
  // codealmanac-known-bugs.md: Engineer B clones a repo that already has
  // `.almanac/pages/` (committed by Engineer A) and gets told to run
  // `almanac init`, which is wrong — the wiki already exists.
  const wikiState = readSetupWikiState(cwd);
  printNextSteps(out, theme, wikiState.existingPageCount, nextStepsMode);

  return { stdout: "", stderr: "", exitCode: 0 };
}
