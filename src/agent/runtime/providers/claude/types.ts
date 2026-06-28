import type {
  Options as ClaudeOptions,
  SDKMessage,
} from "@anthropic-ai/claude-agent-sdk";

export type ClaudeQuery = AsyncIterable<SDKMessage>;

export type ClaudeQueryFn = (params: {
  prompt: string;
  options?: ClaudeOptions;
}) => ClaudeQuery;

export interface ClaudeTraceState {
  sessionId?: string;
  agentParents: Record<string, string | null>;
  agentLabels: Record<string, string>;
  completedAgents: Record<string, boolean>;
}
