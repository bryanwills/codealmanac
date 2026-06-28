import { Command } from "commander";
import { homedir } from "node:os";

import { emit, shouldUseStdoutColor } from "./helpers.js";
import { readDiagnosticUpdateStatus } from "../../services/diagnostics/index.js";
import { probeDiagnosticAutomation } from "../../platform/diagnostics/automation.js";
import { probeDiagnosticClaudeAuth } from "../../platform/diagnostics/auth.js";
import { probeDiagnosticInstall } from "../../platform/diagnostics/install.js";
import {
  probeDiagnosticGuides,
  probeDiagnosticInstructionEntries,
} from "../../platform/diagnostics/instructions.js";

export interface RegisterDoctorCommandDeps {
  runDoctor?: typeof import("../../cli/commands/doctor/index.js").runDoctor;
}

export function registerDoctorCommand(
  program: Command,
  deps: RegisterDoctorCommandDeps = {},
): void {
  program
    .command("doctor")
    .description("report on the Almanac install + current wiki health")
    .option("--json", "emit structured JSON")
    .option("--install-only", "report only on the install (skip wiki checks)")
    .option(
      "--wiki-only",
      "report only on the current wiki (skip install checks)",
    )
    .action(
      async (opts: {
        json?: boolean;
        installOnly?: boolean;
        wikiOnly?: boolean;
      }) => {
        const runDoctor = deps.runDoctor ??
          (await import("../../cli/commands/doctor/index.js")).runDoctor;
        const result = await runDoctor({
          cwd: process.cwd(),
          claudeApiKeySet: process.env.ANTHROPIC_API_KEY !== undefined &&
            process.env.ANTHROPIC_API_KEY.length > 0,
          environment: process.env,
          nodeVersion: process.version,
          authStatus: await probeDiagnosticClaudeAuth(),
          automationStatus: await probeDiagnosticAutomation(),
          guideStatus: probeDiagnosticGuides(),
          instructionEntriesStatus: await probeDiagnosticInstructionEntries(),
          updateStatus: await readDiagnosticUpdateStatus(),
          installStatus: probeDiagnosticInstall({ homeDir: homedir() }),
          json: opts.json,
          installOnly: opts.installOnly,
          wikiOnly: opts.wikiOnly,
          color: shouldUseStdoutColor(),
        });
        emit(result);
      },
    );
}
