import { createComposioToolkitSession } from "../composio/runtime.js";
import {
  connectorStatusLabel,
  isActiveConnectorAccount,
} from "../status.js";
import type { ComposioAccountDeps } from "../composio/accounts.js";
import {
  readConfig,
  type GitHubConnectorAccountConfig,
  type GlobalConfig,
} from "../../config/index.js";

export type GitHubSourceObjectKind = "issue" | "pr";

export interface ReadGitHubSourceOptions extends ComposioAccountDeps {
  repo: string;
  number: string;
  kind: GitHubSourceObjectKind;
  account?: string;
}

export async function readGitHubSource(
  options: ReadGitHubSourceOptions,
): Promise<unknown> {
  const config = await (options.readConfig ?? readConfig)();
  const account = selectActiveGitHubAccount(config, options.account);
  const session = await createComposioToolkitSession({
    config,
    toolkit: "github",
    connectedAccountId: account.connected_account_id,
    deps: options,
  });
  return session.execute({
    toolkit: "github",
    endpoint: githubEndpoint(options),
    method: "GET",
  });
}

function selectActiveGitHubAccount(
  config: GlobalConfig,
  requestedAccount: string | undefined,
): GitHubConnectorAccountConfig {
  const alias = requestedAccount ?? config.connectors.github.default_account;
  if (alias === null) {
    throw new Error("GitHub connector account is not configured. Run `almanac connect github` first.");
  }
  const account = config.connectors.github.accounts[alias];
  if (account === undefined) {
    throw new Error(`GitHub connector account '${alias}' is not configured.`);
  }
  if (!isActiveConnectorAccount(account)) {
    throw new Error(
      `GitHub connector account '${alias}' is ${connectorStatusLabel(account.status)}, not ACTIVE. ` +
        "Finish the connection with `almanac connect github --wait` or inspect status with `almanac connect github --status`.",
    );
  }
  return account;
}

function githubEndpoint(options: ReadGitHubSourceOptions): string {
  const [owner, repo, extra] = options.repo.split("/");
  if (
    owner === undefined ||
    repo === undefined ||
    extra !== undefined ||
    !safeGitHubPart(owner) ||
    !safeGitHubPart(repo)
  ) {
    throw new Error("GitHub repo must be in owner/repo form.");
  }
  if (!/^[1-9][0-9]*$/.test(options.number)) {
    throw new Error("GitHub source number must be a positive integer.");
  }
  const type = options.kind === "pr" ? "pulls" : "issues";
  return `/repos/${owner}/${repo}/${type}/${options.number}`;
}

function safeGitHubPart(part: string): boolean {
  return /^[A-Za-z0-9_.-]+$/.test(part);
}
