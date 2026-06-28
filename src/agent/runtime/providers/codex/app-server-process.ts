import { spawnManagedChildProcess } from "../../../../platform/managed-child.js";

export interface CodexAppServerProcess {
  write(message: Record<string, unknown>): void;
  terminateSafely(): Promise<string | undefined>;
}

export function startCodexAppServerProcess(args: {
  command: string;
  commandArgs: string[];
  cwd: string;
  env: NodeJS.ProcessEnv;
  onMessage: (message: unknown) => void;
  onFailure: (message: string) => void;
}): CodexAppServerProcess {
  const managed = spawnManagedChildProcess(args.command, args.commandArgs, {
    cwd: args.cwd,
    env: args.env,
    stdio: ["pipe", "pipe", "pipe"],
  });
  const child = managed.child;
  let stdoutBuf = "";
  let stderr = "";

  const flushLines = (): void => {
    let idx = stdoutBuf.indexOf("\n");
    while (idx !== -1) {
      const rawLine = stdoutBuf.slice(0, idx);
      stdoutBuf = stdoutBuf.slice(idx + 1);
      const line = rawLine.trim();
      if (line.length > 0) {
        try {
          args.onMessage(JSON.parse(line) as unknown);
        } catch {
          // Ignore non-JSON chatter; stderr is captured for failures.
        }
      }
      idx = stdoutBuf.indexOf("\n");
    }
  };

  child.stdout?.on("data", (chunk) => {
    stdoutBuf += chunk.toString("utf8");
    flushLines();
  });
  child.stderr?.on("data", (chunk) => {
    stderr += chunk.toString("utf8");
  });
  child.on("error", (err: NodeJS.ErrnoException) => {
    args.onFailure(
      err.code === "ENOENT" ? `${args.command} not found on PATH` : err.message,
    );
  });
  child.on("close", (code) => {
    flushLines();
    const firstStderr = stderr.trim().split("\n")[0];
    args.onFailure(
      firstStderr !== undefined && firstStderr.length > 0
        ? firstStderr
        : `${args.command} app-server exited ${code ?? 1}`,
    );
  });

  return {
    write: (message) => {
      child.stdin?.write(`${JSON.stringify(message)}\n`);
    },
    terminateSafely: () => terminateManagedChildSafely(managed),
  };
}

export function installCodexAppServerSignalHandlers(
  onSignal: (signal: NodeJS.Signals) => void,
): () => void {
  const signals: NodeJS.Signals[] = ["SIGINT", "SIGTERM", "SIGHUP"];
  const handlers = signals.map((signal) => {
    const handler = () => onSignal(signal);
    process.once(signal, handler);
    return { signal, handler };
  });
  return () => {
    for (const { signal, handler } of handlers) {
      process.off(signal, handler);
    }
  };
}

async function terminateManagedChildSafely(
  managed: ReturnType<typeof spawnManagedChildProcess>,
): Promise<string | undefined> {
  try {
    await managed.terminate({ graceMs: 500 });
    return undefined;
  } catch (err: unknown) {
    return `Provider process cleanup failed: ${
      err instanceof Error ? err.message : String(err)
    }`;
  }
}
