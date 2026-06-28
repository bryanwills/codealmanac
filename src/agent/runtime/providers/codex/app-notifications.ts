import type { AgentRuntimeEvent } from "../../../../shared/agent-runtime/events.js";
import {
  mapCodexAgentMessageCompletion,
  mapCodexAgentMessageDelta,
} from "./app-agent-messages.js";
import {
  mapCodexErrorNotification,
  mapCodexTurnCompleted,
  mapCodexWarningNotification,
} from "./app-terminal-events.js";
import {
  actorForCodexThread,
  codexLifecycleEvents,
} from "./actors.js";
import {
  asRecord,
  stringField,
} from "./fields.js";
import {
  codexItemDisplay,
  codexItemToToolEvent,
} from "./tool-display.js";
import type {
  CodexRunState,
  JsonRpcNotification,
} from "./types.js";
import { parseCodexAppServerUsage } from "./usage.js";

export function mapCodexAppServerNotification(
  notification: JsonRpcNotification,
  state: CodexRunState,
  context: {
    activeTurnId?: string;
    rootThreadId?: string;
    rootTurnId?: string;
    isRootCompletion?: boolean;
  } = {},
): AgentRuntimeEvent[] {
  const params = asRecord(notification.params);
  const threadId = stringField(params, "threadId");
  const turnId = stringField(params, "turnId");
  const actor = actorForCodexThread(state, threadId, context.rootThreadId);
  if (state.providerSessionId === undefined && threadId !== undefined) {
    state.providerSessionId = threadId;
  }

  if (notification.method === "item/agentMessage/delta") {
    return mapCodexAgentMessageDelta(params, actor);
  }

  if (notification.method === "item/plan/delta") {
    const delta = stringField(params, "delta");
    return delta !== undefined ? [{ type: "tool_summary", summary: delta, actor }] : [];
  }

  if (notification.method === "turn/plan/updated") {
    const explanation = stringField(params, "explanation");
    const plan = Array.isArray(params.plan)
      ? params.plan
          .map((step) => stringField(asRecord(step), "step"))
          .filter((step): step is string => step !== undefined)
      : [];
    const summary = [explanation, ...plan].filter(Boolean).join(" | ");
    return summary.length > 0 ? [{ type: "tool_summary", summary, actor }] : [];
  }

  if (notification.method === "thread/tokenUsage/updated") {
    const usage = parseCodexAppServerUsage(params.tokenUsage);
    if (usage !== undefined) state.usage = usage;
    return usage !== undefined ? [{ type: "context_usage", usage, actor }] : [];
  }

  if (notification.method === "item/started") {
    const item = asRecord(params.item);
    const mapped = codexItemToToolEvent(item, "started", actor, { threadId, turnId });
    const lifecycle = codexLifecycleEvents(state, item, actor, "started");
    return [mapped, ...lifecycle].filter((event): event is AgentRuntimeEvent => event !== undefined);
  }

  if (notification.method === "item/completed") {
    const item = asRecord(params.item);
    if (item.type === "agentMessage") {
      return mapCodexAgentMessageCompletion({
        item,
        state,
        threadId,
        turnId,
        actor,
      });
    }
    const display = codexItemDisplay(item, "completed", { threadId, turnId });
    if (display === undefined) return [];
    const events: AgentRuntimeEvent[] = [
      {
        type: "tool_result",
        id: stringField(item, "id"),
        content: item.aggregatedOutput ?? item.result ?? item.error,
        isError:
          display.status === "failed" ||
            (typeof item.success === "boolean" && item.success === false),
        display,
        actor,
      },
    ];
    events.push(...codexLifecycleEvents(state, item, actor, "completed"));
    return events;
  }

  if (
    notification.method === "item/commandExecution/outputDelta" ||
    notification.method === "command/exec/outputDelta" ||
    notification.method === "item/fileChange/outputDelta"
  ) {
    const delta =
      stringField(params, "delta") ?? decodeBase64(stringField(params, "deltaBase64"));
    return delta !== undefined && delta.trim().length > 0
      ? [{ type: "tool_summary", summary: delta.trim(), actor }]
      : [];
  }

  if (notification.method === "turn/completed") {
    return mapCodexTurnCompleted({
      params,
      state,
      actor,
      activeTurnId: context.activeTurnId,
      isRootCompletion: context.isRootCompletion,
    });
  }

  if (notification.method === "warning") {
    return mapCodexWarningNotification({ params, actor });
  }

  if (notification.method === "error") {
    return mapCodexErrorNotification({ params, state, actor });
  }

  return [];
}

function decodeBase64(value: string | undefined): string | undefined {
  if (value === undefined) return undefined;
  try {
    return Buffer.from(value, "base64").toString("utf8");
  } catch {
    return undefined;
  }
}
