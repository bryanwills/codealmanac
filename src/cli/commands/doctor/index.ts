import { gatherDoctorReport } from "../../../services/diagnostics/index.js";
import type {
  Check,
  CheckStatus,
  DoctorOptions,
  DoctorReport,
  DoctorResult,
  SqliteProbeResult,
} from "../../../services/diagnostics/index.js";
import { renderDoctorReport } from "./render.js";

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
 * This file adapts the diagnostics service report to the CLI command.
 */
export async function runDoctor(
  options: DoctorOptions,
): Promise<DoctorResult> {
  const report = await gatherDoctorReport(options);
  return renderDoctorReport(report, options);
}
