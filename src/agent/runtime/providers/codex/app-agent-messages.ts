import type {
  AgentRuntimeEvent,
  RunActor,
} from "../../../../shared/agent-runtime/events.js";
import { parseJsonSchemaFinalOutputText } from "../../../../shared/agent-runtime/final-output.js";
import { markAgentCompleted } from "./actors.js";
import { stringField } from "./fields.js";
import type { CodexRunState } from "./types.js";

export function mapCodexAgentMessageDelta(
  params: Record<string, unknown>,
  actor: RunActor,
): AgentRuntimeEvent[] {
  const delta = stringField(params, "delta");
  return delta !== undefined ? [{ type: "text_delta", content: delta, actor }] : [];
}

export function mapCodexAgentMessageCompletion(args: {
  item: Record<string, unknown>;
  state: CodexRunState;
  threadId?: string;
  turnId?: string;
  actor: RunActor;
}): AgentRuntimeEvent[] {
  const text = stringField(args.item, "text");
  if (text === undefined) return [];

  const role = args.actor.role;
  if (role === "root") {
    recordRootAgentMessage({
      state: args.state,
      text,
      threadId: args.threadId,
      turnId: args.turnId,
    });
  }

  const events: AgentRuntimeEvent[] = [
    { type: "text", content: text, actor: args.actor },
  ];
  if (
    role === "root" &&
    args.state.failure?.code === "codex.structured_output_invalid"
  ) {
    events.push({
      type: "error",
      error: args.state.failure.message,
      failure: args.state.failure,
      actor: args.actor,
    });
  }
  if (role === "helper" && args.threadId !== undefined) {
    markAgentCompleted(args.state, args.threadId);
    events.push({
      type: "agent_completed",
      threadId: args.threadId,
      parentThreadId: args.state.agentParents?.[args.threadId] ?? null,
      result: text,
      actor: args.actor,
    });
  }
  return events;
}

function recordRootAgentMessage(args: {
  state: CodexRunState;
  text: string;
  threadId?: string;
  turnId?: string;
}): void {
  args.state.result = args.text;
  args.state.resultSourceThreadId = args.threadId;
  args.state.resultSourceTurnId = args.turnId;
  args.state.resultSourceRole = "root";
  if (args.state.outputSpec?.kind !== "json_schema") return;

  try {
    args.state.output = parseJsonSchemaFinalOutputText(
      args.state.outputSpec,
      args.text,
    );
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    args.state.error = message;
    args.state.failure = {
      provider: "codex",
      code: "codex.structured_output_invalid",
      message,
      raw: args.text,
      details: { output: args.state.outputSpec.name },
    };
  }
}
