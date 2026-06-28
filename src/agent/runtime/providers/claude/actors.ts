import type { SDKMessage } from "@anthropic-ai/claude-agent-sdk";

import type { RunActor } from "../../../../shared/agent-runtime/events.js";
import type { ClaudeTraceState } from "./types.js";

export function rootClaudeActor(sessionId: string | undefined): RunActor {
  return {
    threadId: sessionId ?? null,
    role: sessionId === undefined ? "unknown" : "root",
    confidence: sessionId === undefined ? "unknown" : "provider",
    label: sessionId === undefined ? "Unknown actor" : "Main",
  };
}

export function getClaudeSessionId(message: SDKMessage): string | undefined {
  return "session_id" in message && typeof message.session_id === "string"
    ? message.session_id
    : undefined;
}

export function actorForClaudeMessage(
  message: SDKMessage,
  trace: ClaudeTraceState,
): RunActor {
  const sessionId = getClaudeSessionId(message) ?? trace.sessionId;
  trace.sessionId = trace.sessionId ?? sessionId;
  const parentToolUseId = parentToolUseIdFromClaudeMessage(message);
  if (parentToolUseId === null) {
    return rootClaudeActor(sessionId);
  }
  rememberClaudeHelper(trace, parentToolUseId, sessionId ?? null);
  return {
    threadId: parentToolUseId,
    role: "helper",
    parentThreadId: trace.agentParents[parentToolUseId] ?? null,
    confidence: "derived",
    label: trace.agentLabels[parentToolUseId],
  };
}

export function actorForClaudeHelper(
  trace: ClaudeTraceState,
  toolUseId: string,
): RunActor {
  return {
    threadId: toolUseId,
    role: "helper",
    parentThreadId: trace.agentParents[toolUseId] ?? trace.sessionId ?? null,
    confidence: "derived",
    label: trace.agentLabels[toolUseId] ?? helperLabel(trace, toolUseId),
  };
}

export function parentToolUseIdFromClaudeMessage(
  message: SDKMessage,
): string | null {
  if (!("parent_tool_use_id" in message)) return null;
  const value = message.parent_tool_use_id;
  return typeof value === "string" && value.length > 0 ? value : null;
}

export function rememberClaudeHelper(
  trace: ClaudeTraceState,
  toolUseId: string,
  parentThreadId: string | null,
): void {
  trace.agentParents[toolUseId] = trace.agentParents[toolUseId] ?? parentThreadId;
  trace.agentLabels[toolUseId] =
    trace.agentLabels[toolUseId] ?? helperLabel(trace, toolUseId);
}

function helperLabel(trace: ClaudeTraceState, id: string): string {
  const existing = trace.agentLabels[id];
  if (existing !== undefined) return existing;
  const label = `Helper ${Object.keys(trace.agentLabels).length + 1}`;
  trace.agentLabels[id] = label;
  return label;
}
