import type {
  AgentRuntimeEvent,
  AgentRuntimeResult,
  AgentRuntimeRunHooks,
} from "../../../shared/agent-runtime/events.js";
import type { OperationSpec } from "../../../shared/operation-spec.js";

export type JobAgentRunner = (
  spec: OperationSpec,
  hooks?: AgentRuntimeRunHooks,
) => Promise<AgentRuntimeResult>;

export type JobAgentEventHandler = (
  event: AgentRuntimeEvent,
) => void | Promise<void>;
