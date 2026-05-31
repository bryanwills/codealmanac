import { describe, expect, it } from "vitest";

import {
  listGitHubConnections,
  resolveComposioApiKey,
  startGitHubConnection,
  type ComposioClientLike,
} from "../src/connectors/composio/accounts.js";
import { defaultConfig, readConfig } from "../src/config/index.js";
import { withTempHome } from "./helpers.js";

describe("Composio connector accounts", () => {
  it("reads the Composio API key from the configured env var", () => {
    expect(resolveComposioApiKey(defaultConfig(), {
      COMPOSIO_API_KEY: "key_123",
    })).toBe("key_123");
  });

  it("requires a Composio API key", () => {
    expect(() => resolveComposioApiKey(defaultConfig(), {})).toThrow(
      "Composio API key is required",
    );
  });

  it("starts and stores a GitHub connection through Composio", async () => {
    await withTempHome(async () => {
      const fake = fakeComposioClient({
        authConfigs: [{ id: "ac_github" }],
        link: {
          id: "ca_work",
          status: "INITIATED",
          redirectUrl: "https://composio.dev/connect/ca_work",
        },
      });

      const result = await startGitHubConnection({
        account: "work",
        env: { COMPOSIO_API_KEY: "key_123" },
        createClient: () => fake,
      });

      expect(result).toMatchObject({
        account: {
          alias: "work",
          connected_account_id: "ca_work",
          status: "INITIATED",
        },
        redirectUrl: "https://composio.dev/connect/ca_work",
      });
      expect(fake.calls).toEqual([
        "authConfigs.list:github",
        "connectedAccounts.link:work:true",
      ]);
      await expect(readConfig()).resolves.toMatchObject({
        connectors: {
          composio: {
            user_id: expect.stringMatching(/^almanac-/),
          },
          github: {
            default_account: "work",
            accounts: {
              work: {
                connected_account_id: "ca_work",
              },
            },
          },
        },
      });
    });
  });

  it("creates a managed GitHub auth config when none exists", async () => {
    await withTempHome(async () => {
      const fake = fakeComposioClient({
        authConfigs: [],
        createdAuthConfigId: "ac_created",
        link: {
          id: "ca_personal",
          status: "INITIATED",
          redirectUrl: "https://composio.dev/connect/ca_personal",
        },
      });

      await startGitHubConnection({
        account: "personal",
        env: { COMPOSIO_API_KEY: "key_123" },
        createClient: () => fake,
      });

      expect(fake.calls).toContain("authConfigs.create:github:GitHub Auth Config");
      expect(fake.calls).toContain("connectedAccounts.link:personal:true");
    });
  });

  it("lists and stores GitHub connections", async () => {
    await withTempHome(async () => {
      const fake = fakeComposioClient({
        accounts: [
          {
            id: "ca_work",
            alias: "work",
            status: "ACTIVE",
            toolkitSlug: "github",
          },
        ],
      });

      await expect(listGitHubConnections({
        env: { COMPOSIO_API_KEY: "key_123" },
        createClient: () => fake,
      })).resolves.toEqual([
        {
          alias: "work",
          connected_account_id: "ca_work",
          status: "ACTIVE",
        },
      ]);

      await expect(readConfig()).resolves.toMatchObject({
        connectors: {
          github: {
            accounts: {
              work: {
                connected_account_id: "ca_work",
                status: "ACTIVE",
              },
            },
          },
        },
      });
    });
  });
});

function fakeComposioClient(args: {
  authConfigs?: Array<{ id: string }>;
  createdAuthConfigId?: string;
  link?: {
    id: string;
    status: string;
    redirectUrl: string;
  };
  accounts?: Array<{
    id: string;
    alias?: string;
    status?: string;
    toolkitSlug?: string;
  }>;
}): ComposioClientLike & { calls: string[] } {
  const calls: string[] = [];
  return {
    calls,
    authConfigs: {
      async list(query) {
        calls.push(`authConfigs.list:${query.toolkit}`);
        return { items: args.authConfigs ?? [{ id: "ac_github" }] };
      },
      async create(toolkit, options) {
        calls.push(`authConfigs.create:${toolkit}:${options.name}`);
        return { id: args.createdAuthConfigId ?? "ac_created" };
      },
    },
    connectedAccounts: {
      async link(_userId, _authConfigId, options) {
        calls.push(`connectedAccounts.link:${options.alias}:${options.allowMultiple}`);
        return args.link ?? {
          id: "ca_default",
          status: "INITIATED",
          redirectUrl: "https://composio.dev/connect/ca_default",
        };
      },
      async list(query) {
        calls.push(
          `connectedAccounts.list:${query.userIds.length}:${query.toolkitSlugs.join(",")}`,
        );
        return { items: args.accounts ?? [] };
      },
      async get(id) {
        calls.push(`connectedAccounts.get:${id}`);
        return { id, status: "ACTIVE" };
      },
    },
  };
}
