import { spawn, type ChildProcess, type SpawnOptions } from "node:child_process";

const DEFAULT_GRACE_MS = 2_000;

export interface TerminateManagedChildOptions {
  signal?: NodeJS.Signals;
  killSignal?: NodeJS.Signals;
  graceMs?: number;
}

export interface ManagedChildProcess {
  child: ChildProcess;
  readonly treeId?: number;
  terminate(options?: TerminateManagedChildOptions): Promise<void>;
  attachAbort(
    signal: AbortSignal,
    options?: TerminateManagedChildOptions,
  ): () => void;
}

export type ManagedChildSpawnOptions = Omit<SpawnOptions, "detached">;

export function spawnManagedChildProcess(
  command: string,
  args: readonly string[],
  options: ManagedChildSpawnOptions,
): ManagedChildProcess {
  const platform = process.platform === "win32" ? "win32" : "posix";
  const child = spawn(command, [...args], {
    ...options,
    detached: platform === "posix",
  });
  const treeId = child.pid;

  const terminate = (terminateOptions?: TerminateManagedChildOptions) =>
    platform === "posix"
      ? terminatePosixProcessTree(child, treeId, terminateOptions)
      : terminateWindowsProcessTree(child, terminateOptions);

  return {
    child,
    treeId,
    terminate,
    attachAbort: (signal, abortOptions) =>
      attachAbortSignal(signal, child, terminate, abortOptions),
  };
}

async function terminatePosixProcessTree(
  child: ChildProcess,
  treeId: number | undefined,
  options: TerminateManagedChildOptions = {},
): Promise<void> {
  const signal = options.signal ?? "SIGTERM";
  const killSignal = options.killSignal ?? "SIGKILL";
  const graceMs = options.graceMs ?? DEFAULT_GRACE_MS;

  if (!hasExited(child) || isPosixProcessTreeAlive(treeId)) {
    sendPosixProcessTreeSignal(treeId, signal);
  }
  await waitForExit(() => !isPosixProcessTreeAlive(treeId), graceMs);
  if (!isPosixProcessTreeAlive(treeId)) return;
  sendPosixProcessTreeSignal(treeId, killSignal);
  await waitForExit(() => !isPosixProcessTreeAlive(treeId), graceMs);
  if (isPosixProcessTreeAlive(treeId)) {
    throw new Error("managed child process tree did not exit after SIGKILL");
  }
}

async function terminateWindowsProcessTree(
  child: ChildProcess,
  options: TerminateManagedChildOptions = {},
): Promise<void> {
  const signal = options.signal ?? "SIGTERM";
  const graceMs = options.graceMs ?? DEFAULT_GRACE_MS;

  if (hasExited(child)) return;
  child.kill(signal);
  await waitForExit(() => hasExited(child), graceMs);
  if (hasExited(child)) return;
  await runTaskkillTree(child.pid);
  await waitForExit(() => hasExited(child), graceMs);
  if (!hasExited(child)) {
    throw new Error("managed child process tree did not exit after taskkill");
  }
}

function attachAbortSignal(
  signal: AbortSignal,
  child: ChildProcess,
  terminate: (options?: TerminateManagedChildOptions) => Promise<void>,
  options?: TerminateManagedChildOptions,
): () => void {
  if (signal.aborted) {
    void terminate(options).catch(() => undefined);
    return () => undefined;
  }
  const abort = () => {
    void terminate(options).catch(() => undefined);
  };
  signal.addEventListener("abort", abort, { once: true });
  const remove = () => signal.removeEventListener("abort", abort);
  child.once("exit", remove);
  child.once("error", remove);
  return remove;
}

function sendPosixProcessTreeSignal(
  treeId: number | undefined,
  signal: NodeJS.Signals,
): boolean {
  if (treeId === undefined) return false;
  try {
    process.kill(-treeId, signal);
    return true;
  } catch (err: unknown) {
    if (isProcessMissingError(err)) return false;
    throw err;
  }
}

function isPosixProcessTreeAlive(treeId: number | undefined): boolean {
  if (treeId === undefined) return false;
  try {
    process.kill(-treeId, 0);
    return true;
  } catch (err: unknown) {
    if (isProcessMissingError(err)) return false;
    throw err;
  }
}

function hasExited(child: ChildProcess): boolean {
  return child.exitCode !== null || child.signalCode !== null;
}

async function runTaskkillTree(pid: number | undefined): Promise<void> {
  if (pid === undefined) return;
  await new Promise<void>((resolve, reject) => {
    const taskkill = spawn("taskkill", ["/PID", String(pid), "/T", "/F"], {
      stdio: "ignore",
      windowsHide: true,
    });
    taskkill.once("error", reject);
    taskkill.once("close", (code) => {
      if (code === 0) {
        resolve();
        return;
      }
      reject(new Error(`taskkill exited ${code ?? 1}`));
    });
  });
}

async function waitForExit(
  exited: () => boolean,
  timeoutMs: number,
): Promise<boolean> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (exited()) return true;
    await new Promise((resolve) => setTimeout(resolve, 25));
  }
  return exited();
}

function isProcessMissingError(err: unknown): boolean {
  return (
    typeof err === "object" &&
    err !== null &&
    "code" in err &&
    err.code === "ESRCH"
  );
}
