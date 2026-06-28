import { spawn, spawnSync, type ChildProcess } from "node:child_process";

export interface CliStatusResult {
  ok: boolean;
  detail: string;
}

export interface CliStatusSpawnedProcess {
  stdout: { on: (event: "data", cb: (data: Buffer | string) => void) => void };
  stderr: { on: (event: "data", cb: (data: Buffer | string) => void) => void };
  on: (event: "close" | "error", cb: (arg: number | null | Error) => void) => void;
  kill: (signal?: string) => void;
}

export type CliStatusSpawnFn = (args: string[]) => CliStatusSpawnedProcess;

export interface RunCliStatusOptions {
  timeoutMs?: number | null;
}

const DEFAULT_STATUS_TIMEOUT_MS = 3_000;

export function commandExists(command: string): boolean {
  const result = spawnSync("sh", ["-lc", `command -v ${command}`], {
    encoding: "utf8",
  });
  return result.status === 0 && result.stdout.trim().length > 0;
}

export function runInjectedStatusCommand(
  spawnCli: CliStatusSpawnFn,
  args: string[],
  command: string,
): Promise<CliStatusResult> {
  return new Promise((resolve) => {
    let stdout = "";
    let stderr = "";
    let settled = false;
    const settle = (value: CliStatusResult): void => {
      if (settled) return;
      settled = true;
      resolve(value);
    };
    try {
      const child = spawnCli([command, ...args]);
      child.stdout.on("data", (chunk) => {
        stdout += chunk.toString();
      });
      child.stderr.on("data", (chunk) => {
        stderr += chunk.toString();
      });
      child.on("error", (err) => {
        settle({
          ok: false,
          detail: err instanceof Error ? err.message : String(err),
        });
      });
      child.on("close", (code) => {
        const text = `${stdout}\n${stderr}`.trim();
        settle({
          ok: code === 0,
          detail:
            text
              .split("\n")
              .find((line) => line.trim().length > 0)
              ?.trim() ?? (code === 0 ? "ready" : `${command} exited ${code ?? 1}`),
        });
      });
    } catch (err: unknown) {
      settle({
        ok: false,
        detail: err instanceof Error ? err.message : String(err),
      });
    }
  });
}

export function runStatusCommand(
  command: string,
  args: string[],
  options: RunCliStatusOptions = {},
): Promise<CliStatusResult> {
  return new Promise((resolve) => {
    let stdout = "";
    let stderr = "";
    let child: ChildProcess;
    let settled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;
    const settle = (value: CliStatusResult): void => {
      if (settled) return;
      settled = true;
      if (timer !== null) clearTimeout(timer);
      resolve(value);
    };
    try {
      child = spawn(command, args, { stdio: ["ignore", "pipe", "pipe"] });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      resolve({ ok: false, detail: msg });
      return;
    }
    const timeoutMs = options.timeoutMs === undefined
      ? DEFAULT_STATUS_TIMEOUT_MS
      : options.timeoutMs;
    if (timeoutMs !== null) {
      timer = setTimeout(() => {
        try {
          child.kill("SIGTERM");
          setTimeout(() => {
            if (child.exitCode === null && child.signalCode === null) {
              try {
                child.kill("SIGKILL");
              } catch {
                // already exited
              }
            }
          }, 500).unref();
        } catch {
          // already exited
        }
        settle({ ok: false, detail: `${command} status timed out` });
      }, timeoutMs);
    }
    child.stdout?.on("data", (chunk) => {
      stdout += chunk.toString("utf8");
    });
    child.stderr?.on("data", (chunk) => {
      stderr += chunk.toString("utf8");
    });
    child.on("error", (err) => {
      settle({ ok: false, detail: err.message });
    });
    child.on("close", (code) => {
      const text = `${stdout}\n${stderr}`.trim();
      settle({
        ok: code === 0,
        detail:
          text
            .split("\n")
            .find((line) => line.trim().length > 0)
            ?.trim() ?? (code === 0 ? "ready" : `${command} exited ${code ?? 1}`),
      });
    });
  });
}
