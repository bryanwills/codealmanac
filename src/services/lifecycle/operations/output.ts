import type { JobOperationOutput } from "../../../stores/jobs/types.js";
import {
  ALMANAC_OPERATION_REPORT_NAME,
  parseAlmanacOperationReport,
} from "./reports.js";

export function summarizeOperationOutput(
  output: JobOperationOutput | undefined,
): string | undefined {
  if (output?.contract !== ALMANAC_OPERATION_REPORT_NAME) return undefined;
  return parseAlmanacOperationReport(output.value).summary;
}
