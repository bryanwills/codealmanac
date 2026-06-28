import type { AgentRuntimeProvider } from "../types.js";
import { AGENT_RUNTIME_PROVIDER_METADATA } from "./metadata.js";
import { createNotImplementedProvider } from "./not-implemented.js";

export const cursorAgentRuntimeProvider: AgentRuntimeProvider = createNotImplementedProvider(
  AGENT_RUNTIME_PROVIDER_METADATA.cursor,
);
