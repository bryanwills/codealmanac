import type { GitHubConnectorAccountConfig } from "../config/index.js";

export const ACTIVE_CONNECTOR_STATUS = "ACTIVE";

export function isActiveConnectorAccount(
  account: Pick<GitHubConnectorAccountConfig, "status">,
): boolean {
  return account.status === ACTIVE_CONNECTOR_STATUS;
}

export function connectorStatusLabel(status: string | null): string {
  return status ?? "UNKNOWN";
}
