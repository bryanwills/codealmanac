import {
  createComposioClient,
  resolveComposioApiKey,
  type ComposioAccountDeps,
} from "./accounts.js";
import type { GlobalConfig } from "../../config/index.js";

export interface ComposioRuntimeSession {
  execute(args: {
    toolkit: string;
    endpoint: string;
    method: "GET";
  }): Promise<unknown>;
}

export async function createComposioToolkitSession(args: {
  config: GlobalConfig;
  toolkit: "github";
  connectedAccountId: string;
  deps: ComposioAccountDeps;
}): Promise<ComposioRuntimeSession> {
  const apiKey = resolveComposioApiKey(args.config, args.deps.env);
  const userId = args.config.connectors.composio.user_id;
  if (userId === null) {
    throw new Error("Composio user id is not configured. Run `almanac connect github` first.");
  }
  const client = await createComposioClient(apiKey, args.deps.createClient);
  if (client.create === undefined) {
    throw new Error("Installed Composio SDK does not support session proxy execution.");
  }
  const session = await client.create(userId, {
    toolkits: [args.toolkit],
    connectedAccounts: {
      [args.toolkit]: args.connectedAccountId,
    },
  });
  return {
    execute(params) {
      return session.proxyExecute(params);
    },
  };
}
