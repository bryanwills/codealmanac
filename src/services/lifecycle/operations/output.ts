import type { OperationOutput } from "../../../shared/operation-output.js";
import {
  ALMANAC_OPERATION_REPORT_NAME,
  parseAlmanacOperationReport,
} from "./reports.js";

export function summarizeOperationOutput(
  output: OperationOutput | undefined,
): string | undefined {
  if (output?.contract !== ALMANAC_OPERATION_REPORT_NAME) return undefined;
  return parseAlmanacOperationReport(output.value).summary;
}
