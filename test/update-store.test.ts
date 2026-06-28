import { readFile } from "node:fs/promises";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import {
  acquireUpdateLock,
  readStateSync,
  writeState,
} from "../src/stores/update/index.js";
import { withTempHome } from "./helpers.js";

describe("update store", () => {
  it("writes the explicit owner pid into the update lock", async () => {
    await withTempHome(async (home) => {
      const lockPath = join(home, ".almanac", ".update-install.lock");

      const lock = await acquireUpdateLock({ path: lockPath, pid: 12345 });

      expect(lock).not.toBeNull();
      const raw = JSON.parse(await readFile(lockPath, "utf8")) as {
        pid?: unknown;
      };
      expect(raw.pid).toBe(12345);
      await lock?.release();
    });
  });

  it("reads update state synchronously for the pre-command banner", async () => {
    await withTempHome(async (home) => {
      const statePath = join(home, ".almanac", "update-state.json");
      await writeState(
        {
          last_check_at: 1_700_000_000,
          installed_version: "0.2.26",
          latest_version: "0.2.27",
          dismissed_versions: [],
        },
        statePath,
      );

      expect(readStateSync(statePath)).toMatchObject({
        installed_version: "0.2.26",
        latest_version: "0.2.27",
      });
    });
  });
});
