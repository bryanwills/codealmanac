import { describe, expect, it } from "vitest";

import { runSourceGitHub } from "../src/cli/commands/source.js";
import type { ComposioClientLike } from "../src/connectors/composio/accounts.js";
import { writeConfig } from "../src/config/index.js";
import { withTempHome } from "./helpers.js";

describe("source command", () => {
  it("reads a GitHub issue through Composio proxy execution", async () => {
    await withTempHome(async () => {
      const fake = fakeComposioClient();
      await seedConnection();

      const result = await runSourceGitHub({
        kind: "issue",
        number: "11",
        repo: "owner/repo",
        account: "work",
        env: { COMPOSIO_API_KEY: "key_123" },
        createClient: () => fake,
      });

      expect(result.exitCode).toBe(0);
      expect(JSON.parse(result.stdout)).toMatchObject({
        status: 200,
        data: { title: "Issue from Composio" },
      });
      expect(fake.calls).toEqual([
        "create:user_123:github:ca_work",
        "proxyExecute:github:GET:/repos/owner/repo/issues/11",
      ]);
    });
  });

  it("reads a GitHub PR through Composio proxy execution", async () => {
    await withTempHome(async () => {
      const fake = fakeComposioClient();
      await seedConnection();

      const result = await runSourceGitHub({
        kind: "pr",
        number: "12",
        repo: "owner/repo",
        env: { COMPOSIO_API_KEY: "key_123" },
        createClient: () => fake,
      });

      expect(result.exitCode).toBe(0);
      expect(fake.calls).toContain("proxyExecute:github:GET:/repos/owner/repo/pulls/12");
    });
  });

  it("reports setup errors when GitHub is not connected", async () => {
    await withTempHome(async () => {
      const result = await runSourceGitHub({
        kind: "issue",
        number: "11",
        repo: "owner/repo",
        env: { COMPOSIO_API_KEY: "key_123" },
        createClient: () => fakeComposioClient(),
      });

      expect(result.exitCode).toBe(1);
      expect(result.stderr).toContain("almanac connect github");
    });
  });

  it("rejects pending GitHub accounts before Composio source execution", async () => {
    await withTempHome(async () => {
      const fake = fakeComposioClient();
      await seedConnection("INITIATED");

      const result = await runSourceGitHub({
        kind: "issue",
        number: "11",
        repo: "owner/repo",
        account: "work",
        env: { COMPOSIO_API_KEY: "key_123" },
        createClient: () => fake,
      });

      expect(result.exitCode).toBe(1);
      expect(result.stderr).toContain("not ACTIVE");
      expect(fake.calls).toEqual([]);
    });
  });
});

async function seedConnection(status = "ACTIVE"): Promise<void> {
  await writeConfig({
    connectors: {
      composio: {
        api_key_env: "COMPOSIO_API_KEY",
        user_id: "user_123",
      },
      github: {
        default_account: "work",
        accounts: {
          work: {
            alias: "work",
            connected_account_id: "ca_work",
            status,
          },
        },
      },
    },
  });
}

function fakeComposioClient(): ComposioClientLike & { calls: string[] } {
  const calls: string[] = [];
  return {
    calls,
    authConfigs: {
      async list() {
        return { items: [] };
      },
      async create() {
        return { id: "ac_github" };
      },
    },
    connectedAccounts: {
      async link() {
        return { id: "ca_work", status: "ACTIVE" };
      },
      async list() {
        return { items: [] };
      },
      async get(id) {
        return { id, status: "ACTIVE" };
      },
    },
    async create(userId, config) {
      calls.push(`create:${userId}:github:${config.connectedAccounts.github}`);
      return {
        async proxyExecute(params) {
          calls.push(
            `proxyExecute:${params.toolkit}:${params.method}:${params.endpoint}`,
          );
          return {
            status: 200,
            data: { title: "Issue from Composio" },
          };
        },
      };
    },
  };
}
