import type { CommandResult } from "../helpers.js";
import { renderOutcome } from "../outcome.js";
import {
  listGitHubConnections,
  startGitHubConnection,
  type ComposioAccountDeps,
} from "../../connectors/composio/accounts.js";
import { isConnectorAlias } from "../../config/index.js";

export interface ConnectGitHubOptions extends ComposioAccountDeps {
  account?: string;
  status?: boolean;
  wait?: boolean;
  json?: boolean;
}

export async function runConnectGitHub(
  options: ConnectGitHubOptions = {},
): Promise<CommandResult> {
  const account = options.account ?? "default";
  if (!isConnectorAlias(account)) {
    return renderOutcome(
      {
        type: "error",
        message:
          "GitHub account alias may contain only letters, numbers, underscores, dots, and hyphens.",
      },
      { json: options.json },
    );
  }
  try {
    if (options.status === true) {
      const accounts = await listGitHubConnections(options);
      return renderAccounts(accounts, options.json);
    }
    const result = await startGitHubConnection({
      ...options,
      account,
    });
    if (options.json === true) {
      return renderOutcome(
        {
          type: "success",
          message: `GitHub connection started for account '${account}'.`,
          data: {
            account: result.account,
            redirectUrl: result.redirectUrl ?? null,
            userId: result.userId,
          },
        },
        { json: true },
      );
    }
    const hasRedirect = result.redirectUrl !== undefined && result.redirectUrl !== null;
    return {
      stdout: [
        `GitHub connection started for account "${account}".`,
        hasRedirect ? "" : null,
        hasRedirect ? "Open this URL to connect GitHub:" : null,
        hasRedirect ? result.redirectUrl : null,
        "",
        "After approving access, check the connection with:",
        "  almanac connect github --status",
        "",
      ].filter((line): line is string => line !== null).join("\n"),
      stderr: "",
      exitCode: 0,
    };
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    if (message.includes("Composio API key is required")) {
      return renderOutcome(
        {
          type: "needs-action",
          message: "GitHub connections use Composio and need a Composio API key.",
          fix: message,
        },
        { json: options.json },
      );
    }
    return renderOutcome(
      { type: "error", message },
      { json: options.json },
    );
  }
}

function renderAccounts(
  accounts: Array<{ alias: string; connected_account_id: string; status: string | null }>,
  json: boolean | undefined,
): CommandResult {
  if (json === true) {
    return {
      stdout: `${JSON.stringify(accounts, null, 2)}\n`,
      stderr: "",
      exitCode: 0,
    };
  }
  if (accounts.length === 0) {
    return {
      stdout: "No GitHub connections found.\n",
      stderr: "",
      exitCode: 0,
    };
  }
  return {
    stdout: accounts
      .map((account) =>
        `${account.alias}\t${account.status ?? "unknown"}\t${account.connected_account_id}`)
      .join("\n") + "\n",
    stderr: "",
    exitCode: 0,
  };
}
