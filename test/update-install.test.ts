import { EventEmitter } from "node:events";
import type { spawn as nodeSpawn } from "node:child_process";

import { describe, expect, it } from "vitest";

import { installLatestPackage } from "../src/platform/update/install.js";

type PlatformSpawnFn = typeof nodeSpawn;

function fakeSpawn(exitCode: number | null): {
  spawnFn: PlatformSpawnFn;
  calls: Array<{
    command: string;
    args: readonly string[];
    options: unknown;
  }>;
} {
  const calls: Array<{
    command: string;
    args: readonly string[];
    options: unknown;
  }> = [];
  const spawnFn = ((command, args, options) => {
    calls.push({
      command,
      args: args ?? [],
      options,
    });
    const emitter = new EventEmitter();
    queueMicrotask(() => {
      emitter.emit("exit", exitCode, null);
    });
    return emitter as ReturnType<PlatformSpawnFn>;
  }) as PlatformSpawnFn;
  return { spawnFn, calls };
}

function fakeSpawnError(code: string): PlatformSpawnFn {
  return (() => {
    const emitter = new EventEmitter();
    queueMicrotask(() => {
      const err = new Error(`spawn npm ${code}`) as NodeJS.ErrnoException;
      err.code = code;
      emitter.emit("error", err);
    });
    return emitter as ReturnType<PlatformSpawnFn>;
  }) as PlatformSpawnFn;
}

describe("installLatestPackage", () => {
  it("spawns npm with the global codealmanac latest install command", async () => {
    const { spawnFn, calls } = fakeSpawn(0);

    const result = await installLatestPackage({ spawnFn });

    expect(result).toEqual({
      stdout: "almanac: updated.\n",
      stderr: "",
      exitCode: 0,
    });
    expect(calls).toEqual([
      {
        command: "npm",
        args: ["i", "-g", "codealmanac@latest"],
        options: { stdio: "inherit" },
      },
    ]);
  });

  it("returns a clear message when npm is not on PATH", async () => {
    const result = await installLatestPackage({
      spawnFn: fakeSpawnError("ENOENT"),
    });

    expect(result.exitCode).toBe(1);
    expect(result.stderr).toContain("`npm` not found on PATH");
  });

  it("returns the npm exit code and permission hint on install failure", async () => {
    const { spawnFn } = fakeSpawn(243);

    const result = await installLatestPackage({ spawnFn });

    expect(result.exitCode).toBe(243);
    expect(result.stderr).toContain("EACCES");
    expect(result.stderr).toContain("sudo npm i -g codealmanac@latest");
  });
});
