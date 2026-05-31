import { randomUUID } from "node:crypto";

import {
  readConfig,
  writeConfig,
  type GlobalConfig,
  type GitHubConnectorAccountConfig,
} from "../../config/index.js";

const GITHUB_TOOLKIT = "github";

export interface ComposioConnectionRequest {
  id: string;
  status?: string;
  redirectUrl?: string | null;
  waitForConnection?: (timeoutMs?: number) => Promise<ComposioConnectedAccount>;
}

export interface ComposioConnectedAccount {
  id: string;
  status?: string;
  toolkit?: { slug?: string };
  toolkitSlug?: string;
  alias?: string | null;
}

export interface ComposioClientLike {
  authConfigs: {
    list(query: { toolkit: string }): Promise<{ items: Array<{ id: string }> }>;
    create(
      toolkit: string,
      options: { type: "use_composio_managed_auth"; name: string },
    ): Promise<{ id: string }>;
  };
  connectedAccounts: {
    link(
      userId: string,
      authConfigId: string,
      options: { alias: string; allowMultiple: boolean },
    ): Promise<ComposioConnectionRequest>;
    list(query: {
      userIds: string[];
      toolkitSlugs: string[];
    }): Promise<{ items: ComposioConnectedAccount[] }>;
    get(id: string): Promise<ComposioConnectedAccount>;
  };
  create?: (
    userId: string,
    config: {
      toolkits: string[];
      connectedAccounts: Record<string, string>;
    },
  ) => Promise<{
    proxyExecute(params: {
      toolkit: string;
      endpoint: string;
      method: "GET";
      parameters?: Array<{ in: "query" | "header"; name: string; value: string | number }>;
    }): Promise<unknown>;
  }>;
}

export interface ComposioAccountDeps {
  createClient?: (apiKey: string) => Promise<ComposioClientLike> | ComposioClientLike;
  env?: Record<string, string | undefined>;
  readConfig?: typeof readConfig;
  writeConfig?: typeof writeConfig;
}

export interface StartGitHubConnectionOptions extends ComposioAccountDeps {
  account: string;
  wait?: boolean;
  timeoutMs?: number;
}

export interface GitHubConnectionResult {
  account: GitHubConnectorAccountConfig;
  redirectUrl?: string | null;
  userId: string;
}

export interface ListGitHubConnectionsOptions extends ComposioAccountDeps {}

export async function startGitHubConnection(
  options: StartGitHubConnectionOptions,
): Promise<GitHubConnectionResult> {
  const read = options.readConfig ?? readConfig;
  const write = options.writeConfig ?? writeConfig;
  const config = await read();
  const apiKey = resolveComposioApiKey(config, options.env);
  const userId = await ensureComposioUserId(config, { read, write });
  const client = await createComposioClient(apiKey, options.createClient);
  const authConfigId = await resolveAuthConfigId(client);
  const request = await client.connectedAccounts.link(userId, authConfigId, {
    alias: options.account,
    allowMultiple: true,
  });
  const connected = options.wait === true && request.waitForConnection !== undefined
    ? await request.waitForConnection(options.timeoutMs)
    : null;
  const account = {
    alias: options.account,
    connected_account_id: connected?.id ?? request.id,
    status: connected?.status ?? request.status ?? "INITIATED",
  };
  await saveGitHubAccount(account, { read, write });
  return {
    account,
    redirectUrl: request.redirectUrl,
    userId,
  };
}

export async function listGitHubConnections(
  options: ListGitHubConnectionsOptions = {},
): Promise<GitHubConnectorAccountConfig[]> {
  const read = options.readConfig ?? readConfig;
  const write = options.writeConfig ?? writeConfig;
  const config = await read();
  const apiKey = resolveComposioApiKey(config, options.env);
  const userId = await ensureComposioUserId(config, { read, write });
  const client = await createComposioClient(apiKey, options.createClient);
  const listed = await client.connectedAccounts.list({
    userIds: [userId],
    toolkitSlugs: [GITHUB_TOOLKIT],
  });
  const accounts = listed.items.map(toGitHubAccountConfig);
  if (accounts.length > 0) await saveGitHubAccounts(accounts, { read, write });
  return accounts;
}

export function resolveComposioApiKey(
  config: GlobalConfig,
  env: Record<string, string | undefined> = process.env,
): string {
  const envName = config.connectors.composio.api_key_env;
  const apiKey = env[envName];
  if (typeof apiKey === "string" && apiKey.length > 0) return apiKey;
  throw new Error(
    `Composio API key is required. Set ${envName} and run this command again.`,
  );
}

async function ensureComposioUserId(
  config: GlobalConfig,
  deps: {
    read: typeof readConfig;
    write: typeof writeConfig;
  },
): Promise<string> {
  const existing = config.connectors.composio.user_id;
  if (existing !== null) return existing;
  const userId = `almanac-${randomUUID()}`;
  await deps.write({
    connectors: {
      ...config.connectors,
      composio: {
        ...config.connectors.composio,
        user_id: userId,
      },
    },
  });
  return userId;
}

export async function createComposioClient(
  apiKey: string,
  createClient: StartGitHubConnectionOptions["createClient"],
): Promise<ComposioClientLike> {
  if (createClient !== undefined) return createClient(apiKey);
  const mod = await import("@composio/core");
  const client = new mod.Composio({ apiKey }) as unknown;
  return client as ComposioClientLike;
}

async function resolveAuthConfigId(client: ComposioClientLike): Promise<string> {
  const existing = await client.authConfigs.list({ toolkit: GITHUB_TOOLKIT });
  const first = existing.items[0]?.id;
  if (first !== undefined) return first;
  const created = await client.authConfigs.create(GITHUB_TOOLKIT, {
    type: "use_composio_managed_auth",
    name: "GitHub Auth Config",
  });
  return created.id;
}

async function saveGitHubAccount(
  account: GitHubConnectorAccountConfig,
  deps: {
    read: typeof readConfig;
    write: typeof writeConfig;
  },
): Promise<void> {
  await saveGitHubAccounts([account], deps);
}

async function saveGitHubAccounts(
  accounts: GitHubConnectorAccountConfig[],
  deps: {
    read: typeof readConfig;
    write: typeof writeConfig;
  },
): Promise<void> {
  const config = await deps.read();
  const mergedAccounts = {
    ...config.connectors.github.accounts,
  };
  for (const account of accounts) {
    mergedAccounts[account.alias] = account;
  }
  const defaultAccount =
    config.connectors.github.default_account ?? accounts[0]?.alias ?? null;
  await deps.write({
    connectors: {
      ...config.connectors,
      github: {
        default_account: defaultAccount,
        accounts: mergedAccounts,
      },
    },
  });
}

function toGitHubAccountConfig(
  account: ComposioConnectedAccount,
): GitHubConnectorAccountConfig {
  return {
    alias: account.alias ?? account.id,
    connected_account_id: account.id,
    status: account.status ?? null,
  };
}
