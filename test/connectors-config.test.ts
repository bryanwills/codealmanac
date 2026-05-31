import { readFile } from "node:fs/promises";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import {
  defaultConfig,
  parseConfigText,
  readConfig,
  serializeConfig,
  writeConfig,
} from "../src/config/index.js";
import { withTempHome } from "./helpers.js";

describe("connector config", () => {
  it("defaults to Composio env auth with no connected accounts", async () => {
    expect(defaultConfig().connectors).toEqual({
      composio: {
        api_key_env: "COMPOSIO_API_KEY",
        user_id: null,
      },
      github: {
        default_account: null,
        accounts: {},
      },
    });
  });

  it("parses and serializes Composio GitHub accounts", () => {
    const raw = parseConfigText([
      "[connectors.composio]",
      'api_key_env = "ALMANAC_COMPOSIO_API_KEY"',
      'user_id = "almanac-local-user"',
      "",
      "[connectors.github]",
      'default_account = "work"',
      "",
      "[connectors.github.accounts.work]",
      'connected_account_id = "ca_work"',
      'status = "ACTIVE"',
    ].join("\n"));

    expect(raw).toMatchObject({
      connectors: {
        composio: {
          api_key_env: "ALMANAC_COMPOSIO_API_KEY",
          user_id: "almanac-local-user",
        },
        github: {
          default_account: "work",
          accounts: {
            work: {
              connected_account_id: "ca_work",
              status: "ACTIVE",
            },
          },
        },
      },
    });

    expect(serializeConfig(raw)).toContain("[connectors.github.accounts.work]");
  });

  it("round trips connector config through writeConfig", async () => {
    await withTempHome(async (home) => {
      await writeConfig({
        connectors: {
          composio: {
            api_key_env: "ALMANAC_COMPOSIO_API_KEY",
            user_id: "almanac-local-user",
          },
          github: {
            default_account: "work",
            accounts: {
              work: {
                alias: "work",
                connected_account_id: "ca_work",
                status: "ACTIVE",
              },
            },
          },
        },
      });

      await expect(readConfig()).resolves.toMatchObject({
        connectors: {
          composio: {
            api_key_env: "ALMANAC_COMPOSIO_API_KEY",
            user_id: "almanac-local-user",
          },
          github: {
            default_account: "work",
            accounts: {
              work: {
                alias: "work",
                connected_account_id: "ca_work",
                status: "ACTIVE",
              },
            },
          },
        },
      });

      const toml = await readFile(join(home, ".almanac", "config.toml"), "utf8");
      expect(toml).toContain("[connectors.composio]");
      expect(toml).toContain('api_key_env = "ALMANAC_COMPOSIO_API_KEY"');
      expect(toml).toContain('user_id = "almanac-local-user"');
      expect(toml).toContain("[connectors.github]");
      expect(toml).toContain('default_account = "work"');
      expect(toml).toContain("[connectors.github.accounts.work]");
      expect(toml).toContain('connected_account_id = "ca_work"');
    });
  });
});
