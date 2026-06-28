import type {
  AgentRuntimeEvent,
  RunActor,
} from "../../../../shared/agent-runtime/events.js";
import { classifyCodexFailure } from "./failures.js";
import {
  asRecord,
  numberField,
  stringField,
} from "./fields.js";
import type { CodexRunState } from "./types.js";

export function mapCodexTurnCompleted(args: {
  params: Record<string, unknown>;
  state: CodexRunState;
  actor: RunActor;
  activeTurnId?: string;
  isRootCompletion?: boolean;
}): AgentRuntimeEvent[] {
  const turn = asRecord(args.params.turn);
  const error = asRecord(turn.error);
  const errorMessage = stringField(error, "message");
  if (errorMessage !== undefined) {
    const failure = classifyCodexFailure({
      message: errorMessage,
      statusCode: numberField(error, "statusCode") ?? numberField(error, "code"),
      data: error,
    });
    if (args.isRootCompletion !== false) {
      args.state.success = false;
      args.state.error = failure.message;
      args.state.failure = failure;
    }
    return [{ type: "error", error: failure.message, failure, actor: args.actor }];
  }
  if (args.isRootCompletion !== false) {
    args.state.success = true;
    args.state.turns = args.activeTurnId !== undefined ? 1 : 1;
  }
  return [];
}

export function mapCodexWarningNotification(args: {
  params: Record<string, unknown>;
  actor: RunActor;
}): AgentRuntimeEvent[] {
  const message = stringField(args.params, "message") ?? "Codex warning";
  return [{ type: "tool_summary", summary: `Warning: ${message}`, actor: args.actor }];
}

export function mapCodexErrorNotification(args: {
  params: Record<string, unknown>;
  state: CodexRunState;
  actor: RunActor;
}): AgentRuntimeEvent[] {
  const error = asRecord(args.params.error);
  const message =
    stringField(error, "message") ??
    stringField(error, "detail") ??
    stringField(args.params, "message") ??
    "Codex error";
  const failure = classifyCodexFailure({
    message,
    statusCode: numberField(error, "statusCode") ?? numberField(error, "code"),
    data: error,
  });
  args.state.success = false;
  args.state.error = failure.message;
  args.state.failure = failure;
  return [{ type: "error", error: failure.message, failure, actor: args.actor }];
}
