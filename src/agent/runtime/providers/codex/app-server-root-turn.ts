import {
  asRecord,
  stringField,
} from "./fields.js";
import type { CodexRunState, JsonRpcNotification } from "./types.js";

export function codexNotificationTurnId(
  message: JsonRpcNotification,
): string | undefined {
  return stringField(asRecord(message.params), "turnId");
}

export function isCodexRootTurnCompletion(args: {
  message: JsonRpcNotification;
  state: CodexRunState;
  activeTurnId: string | undefined;
}): boolean | undefined {
  if (args.message.method !== "turn/completed") return undefined;

  const params = asRecord(args.message.params);
  const completedTurnId = stringField(params, "turnId");
  const completedThreadId = stringField(params, "threadId");
  const isRootTurn =
    (args.state.rootTurnId !== undefined &&
      completedTurnId === args.state.rootTurnId) ||
    (args.state.rootTurnId === undefined &&
      args.activeTurnId !== undefined &&
      completedTurnId === args.activeTurnId);
  const isRootThread =
    args.state.rootThreadId !== undefined &&
    completedThreadId === args.state.rootThreadId;
  return isRootTurn || isRootThread;
}

export function isCodexRootThreadNotification(args: {
  message: JsonRpcNotification;
  state: CodexRunState;
}): boolean {
  const threadId = stringField(asRecord(args.message.params), "threadId");
  return (
    args.state.rootThreadId !== undefined &&
    threadId === args.state.rootThreadId
  );
}
