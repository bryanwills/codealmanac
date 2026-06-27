import { formatReport } from "./format.js";
import { gatherDoctorReport } from "../../../services/diagnostics/index.js";
import type {
  Check,
  CheckStatus,
  DoctorOptions,
  DoctorReport,
  DoctorResult,
  SqliteProbeResult,
} from "../../../services/diagnostics/index.js";

export type {
  Check,
  CheckStatus,
  DoctorOptions,
  DoctorReport,
  DoctorResult,
  SqliteProbeResult,
};

/**
 * `almanac doctor` — install + wiki health report.
 *
 * Separate from `almanac health` (which checks graph integrity of a
 * specific wiki). `doctor` answers the "is this install even set up
 * correctly?" question that users hit when first trying the tool or when
 * sessions silently stop getting absorbed.
 *
 * This file renders the diagnostics service report for the CLI.
 */
export async function runDoctor(
  options: DoctorOptions,
): Promise<DoctorResult> {
  const report = await gatherDoctorReport(options);

  if (options.json === true) {
    return {
      stdout: `${JSON.stringify(report, null, 2)}\n`,
      stderr: "",
      exitCode: 0,
    };
  }

  return {
    stdout: formatReport(report, options),
    stderr: "",
    exitCode: 0,
  };
}
