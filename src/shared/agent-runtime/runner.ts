import type {
  AgentRuntimeEvent,
  AgentRuntimeResult,
  AgentRuntimeRunHooks,
} from "./events.js";
import type { OperationSpec } from "../operation-spec.js";

export type AgentRuntimeRunner = (
  spec: OperationSpec,
  hooks?: AgentRuntimeRunHooks,
) => Promise<AgentRuntimeResult>;

export type AgentRuntimeEventHandler = (
  event: AgentRuntimeEvent,
) => void | Promise<void>;
