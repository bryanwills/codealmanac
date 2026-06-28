import type { JsonRpcNotification } from "./types.js";

interface JsonRpcResponse {
  id: number | string;
  result?: unknown;
  error?: {
    message?: string;
    code?: number;
    data?: unknown;
  };
}

interface PendingRequest {
  resolve: (value: unknown) => void;
  reject: (err: Error) => void;
}

export interface CodexAppServerRpcResponder {
  respond: (id: string | number, result: unknown) => void;
  respondError: (id: string | number, code: number, message: string) => void;
  respondUnsupported: (id: string | number, method: string) => void;
}

export interface CodexAppServerRpcTransport {
  request: (method: string, params?: unknown) => Promise<unknown>;
  receive: (message: unknown) => void;
  rejectPending: (error: Error) => void;
}

export function createCodexAppServerRpcTransport(args: {
  rpcTimeoutMs: number;
  write: (message: Record<string, unknown>) => void;
  onNotification: (message: JsonRpcNotification) => void;
  onServerRequest: (
    id: string | number,
    method: string,
    responder: CodexAppServerRpcResponder,
  ) => void;
}): CodexAppServerRpcTransport {
  let nextRequestId = 1;
  const pending = new Map<string, PendingRequest>();

  const respond = (id: string | number, result: unknown): void => {
    args.write({ id, result });
  };

  const respondError = (id: string | number, code: number, message: string): void => {
    args.write({
      id,
      error: {
        code,
        message,
      },
    });
  };

  const respondUnsupported = (id: string | number, method: string): void => {
    respondError(
      id,
      -32601,
      `Almanac does not handle Codex app-server request ${method}`,
    );
  };

  return {
    request: (method, params) => requestRpc({
      method,
      params,
      rpcTimeoutMs: args.rpcTimeoutMs,
      write: args.write,
      pending,
      nextId: () => nextRequestId++,
    }),
    receive: (message) => receiveMessage(message, {
      pending,
      onNotification: args.onNotification,
      onServerRequest: args.onServerRequest,
      responder: { respond, respondError, respondUnsupported },
    }),
    rejectPending: (error) => {
      for (const entry of pending.values()) {
        entry.reject(error);
      }
      pending.clear();
    },
  };
}

function requestRpc(args: {
  method: string;
  params?: unknown;
  rpcTimeoutMs: number;
  write: (message: Record<string, unknown>) => void;
  pending: Map<string, PendingRequest>;
  nextId: () => number;
}): Promise<unknown> {
  const id = args.nextId();
  return new Promise((requestResolve, requestReject) => {
    const timeout = setTimeout(() => {
      args.pending.delete(String(id));
      requestReject(
        new Error(
          `Codex app-server ${args.method} timed out after ${args.rpcTimeoutMs}ms`,
        ),
      );
    }, args.rpcTimeoutMs);
    args.pending.set(String(id), {
      resolve: (value) => {
        clearTimeout(timeout);
        requestResolve(value);
      },
      reject: (err) => {
        clearTimeout(timeout);
        requestReject(err);
      },
    });
    args.write({
      id,
      method: args.method,
      ...(args.params !== undefined ? { params: args.params } : {}),
    });
  });
}

function receiveMessage(
  message: unknown,
  args: {
    pending: Map<string, PendingRequest>;
    onNotification: (message: JsonRpcNotification) => void;
    onServerRequest: (
      id: string | number,
      method: string,
      responder: CodexAppServerRpcResponder,
    ) => void;
    responder: CodexAppServerRpcResponder;
  },
): void {
  if (message === null || typeof message !== "object") return;
  const record = message as Record<string, unknown>;
  if ("id" in record && "method" in record) {
    args.onServerRequest(
      record.id as string | number,
      String(record.method),
      args.responder,
    );
    return;
  }
  if ("id" in record) {
    handleResponse(record as unknown as JsonRpcResponse, args.pending);
    return;
  }
  if ("method" in record) {
    args.onNotification(record as unknown as JsonRpcNotification);
  }
}

function handleResponse(
  message: JsonRpcResponse,
  pending: Map<string, PendingRequest>,
): void {
  const item = pending.get(String(message.id));
  if (item === undefined) return;
  pending.delete(String(message.id));
  if (message.error !== undefined) {
    item.reject(new Error(message.error.message ?? "Codex app-server request failed"));
    return;
  }
  item.resolve(message.result);
}
