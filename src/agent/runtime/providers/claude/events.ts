import type { SDKMessage } from "@anthropic-ai/claude-agent-sdk";

import type { AgentRuntimeEvent } from "../../../../shared/agent-runtime/events.js";
import type { ClaudeTraceState } from "./types.js";
import {
  actorForClaudeHelper,
  actorForClaudeMessage,
  parentToolUseIdFromClaudeMessage,
  rememberClaudeHelper,
} from "./actors.js";
import {
  promptFromClaudeAgentInput,
  stringifyClaudeInput,
  stringifyClaudeToolResult,
  textDeltaFromClaudeStreamEvent,
} from "./content.js";

export { getClaudeSessionId, rootClaudeActor } from "./actors.js";

export function toClaudeAgentRuntimeEvents(
  message: SDKMessage,
  trace: ClaudeTraceState = {
    agentParents: {},
    agentLabels: {},
    completedAgents: {},
  },
): AgentRuntimeEvent[] {
  const actor = actorForClaudeMessage(message, trace);
  if (message.type === "stream_event") {
    const text = textDeltaFromClaudeStreamEvent(message.event);
    return text !== undefined ? [{ type: "text_delta", content: text, actor }] : [];
  }

  if (message.type === "assistant") {
    const content = message.message.content;
    if (!Array.isArray(content)) return [];
    const events: AgentRuntimeEvent[] = [];
    for (const block of content) {
      if (block.type === "text") {
        events.push({ type: "text", content: block.text, actor });
        continue;
      }
      if (block.type === "tool_use") {
        events.push({
          type: "tool_use",
          id: block.id,
          tool: block.name,
          input: stringifyClaudeInput(block.input),
          actor,
          providerEventId: message.uuid,
          providerParentToolUseId:
            parentToolUseIdFromClaudeMessage(message) ?? undefined,
        });
        if (block.name === "Agent") {
          rememberClaudeHelper(trace, block.id, trace.sessionId ?? null);
          events.push({
            type: "agent_spawned",
            parentThreadId: trace.sessionId ?? "",
            childThreadId: block.id,
            prompt: promptFromClaudeAgentInput(block.input),
            actor,
          });
        }
      }
    }
    return events;
  }

  if (message.type === "user") {
    const content = message.message.content;
    if (!Array.isArray(content)) return [];
    return content.flatMap((block) => {
      if (block.type !== "tool_result") return [];
      const events: AgentRuntimeEvent[] = [
        {
          type: "tool_result",
          id: block.tool_use_id,
          content: block.content,
          isError: block.is_error,
          actor,
          providerEventId: message.uuid,
          providerParentToolUseId:
            parentToolUseIdFromClaudeMessage(message) ?? undefined,
        },
      ];
      if (
        trace.agentParents[block.tool_use_id] !== undefined &&
        trace.completedAgents[block.tool_use_id] !== true
      ) {
        trace.completedAgents[block.tool_use_id] = true;
        const helperActor = actorForClaudeHelper(trace, block.tool_use_id);
        events.push({
          type: "agent_completed",
          threadId: block.tool_use_id,
          parentThreadId:
            trace.agentParents[block.tool_use_id] ?? trace.sessionId ?? null,
          result: stringifyClaudeToolResult(block.content),
          actor: helperActor,
        });
      }
      return events;
    });
  }

  if (message.type === "tool_use_summary") {
    return [{ type: "tool_summary", summary: message.summary, actor }];
  }

  if (message.type === "result" && message.subtype !== "success") {
    return message.errors.map((err) => ({ type: "error", error: err, actor }));
  }

  return [];
}
