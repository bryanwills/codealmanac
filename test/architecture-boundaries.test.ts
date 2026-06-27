import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

const ROOT = process.cwd();

describe("architecture boundaries", () => {
  it("keeps src/cli.ts as a stable facade over the CLI edge runner", async () => {
    const facade = await readSource("src/cli.ts");

    expect(facade).toContain("from \"./edges/cli/run.js\"");
    expect(facade).not.toContain("from \"commander\"");
    expect(facade).not.toContain("cli/commands");
    expect(facade).not.toContain("platform/");
    expect(facade).not.toContain("jobs/");
  });

  it("keeps process-level CLI machinery inside the CLI edge", async () => {
    const runner = await readSource("src/edges/cli/run.ts");

    expect(runner).toContain("from \"commander\"");
    expect(runner).toContain("tryRunInternalJob");
    expect(runner).toContain("readPackageVersion");
  });

  it("keeps CLI registration and shortcut parsing in the CLI edge", () => {
    const oldCliShellFiles = [
      "src/cli/help.ts",
      "src/cli/sqlite-free.ts",
      "src/cli/register-commands.ts",
      "src/cli/register-query-commands.ts",
      "src/cli/register-edit-commands.ts",
      "src/cli/register-setup-commands.ts",
      "src/cli/register-wiki-lifecycle-commands.ts",
    ];

    for (const path of oldCliShellFiles) {
      expect(existsSync(join(ROOT, path)), path).toBe(false);
    }
  });
});

async function readSource(path: string): Promise<string> {
  return readFile(join(ROOT, path), "utf8");
}
