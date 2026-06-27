import { formatReport } from "./format.js";
import type {
  DoctorOptions,
  DoctorReport,
  DoctorResult,
} from "../../../services/diagnostics/index.js";

export function renderDoctorReport(
  report: DoctorReport,
  options: DoctorOptions,
): DoctorResult {
  return {
    stdout: options.json === true
      ? `${JSON.stringify(report, null, 2)}\n`
      : formatReport(report, options),
    stderr: "",
    exitCode: 0,
  };
}
