import { describe, expect, it } from "vitest";

import { runConnectGitHub } from "../src/cli/commands/connect.js";
import type { ComposioClientLike } from "../src/connectors/composio/accounts.js";
import { withTempHome } from "./helpers.js";

describe("connect command", () => {
  it("starts GitHub connection through Composio", async () => {
    await withTempHome(async () => {
      const result = await runConnectGitHub({
        account: "work",
        env: { COMPOSIO_API_KEY: "key_123" },
        createClient: () => fakeComposioClient({
          link: {
            id: "ca_work",
            status: "INITIATED",
            redirectUrl: "https://composio.dev/connect/ca_work",
          },
        }),
      });

      expect(result.exitCode).toBe(0);
      expect(result.stdout).toContain('GitHub connection started for account "work"');
      expect(result.stdout).toContain("https://composio.dev/connect/ca_work");
      expect(result.stdout).toContain("almanac connect github --status");
    });
  });

  it("lists GitHub connection status", async () => {
    await withTempHome(async () => {
      const result = await runConnectGitHub({
        status: true,
        env: { COMPOSIO_API_KEY: "key_123" },
        createClient: () => fakeComposioClient({
          accounts: [
            {
              id: "ca_work",
              alias: "work",
              status: "ACTIVE",
            },
          ],
        }),
      });

      expect(result.exitCode).toBe(0);
      expect(result.stdout).toBe("work\tACTIVE\tca_work\n");
    });
  });

  it("reports missing Composio API key as setup action", async () => {
    await withTempHome(async () => {
      const result = await runConnectGitHub({
        account: "work",
        env: {},
      });

      expect(result.exitCode).toBe(1);
      expect(result.stderr).toContain("GitHub connections use Composio");
      expect(result.stderr).toContain("Set COMPOSIO_API_KEY");
    });
  });

  it("rejects unsafe aliases", async () => {
    const result = await runConnectGitHub({
      account: "../work",
      env: { COMPOSIO_API_KEY: "key_123" },
    });

    expect(result.exitCode).toBe(1);
    expect(result.stderr).toContain("GitHub account alias");
  });
});

function fakeComposioClient(args: {
  link?: {
    id: string;
    status: string;
    redirectUrl: string;
  };
  accounts?: Array<{
    id: string;
    alias?: string;
    status?: string;
  }>;
}): ComposioClientLike {
  return {
    authConfigs: {
      async list() {
        return { items: [{ id: "ac_github" }] };
      },
      async create() {
        return { id: "ac_created" };
      },
    },
    connectedAccounts: {
      async link() {
        return args.link ?? {
          id: "ca_default",
          status: "INITIATED",
          redirectUrl: "https://composio.dev/connect/ca_default",
        };
      },
      async list() {
        return { items: args.accounts ?? [] };
      },
      async get(id) {
        return { id, status: "ACTIVE" };
      },
    },
  };
}
