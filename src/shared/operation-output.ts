import type { JsonValue } from "./agent-runtime/final-output.js";

export interface OperationOutput {
  version: 1;
  contract: string;
  value: JsonValue;
}
