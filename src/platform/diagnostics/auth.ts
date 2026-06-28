import {
  checkClaudeAuth,
  type ClaudeAuthStatus,
} from "../../agent/providers/claude/auth.js";
import type {
  DiagnosticsAuthStatus,
  DiagnosticsSpawnCliFn,
} from "../../shared/diagnostics.js";

export async function probeDiagnosticClaudeAuth(
  spawnCli?: DiagnosticsSpawnCliFn,
): Promise<DiagnosticsAuthStatus> {
  try {
    return diagnosticAuthStatusFromClaude(await checkClaudeAuth(spawnCli));
  } catch {
    return { loggedIn: false };
  }
}

function diagnosticAuthStatusFromClaude(
  auth: ClaudeAuthStatus,
): DiagnosticsAuthStatus {
  return {
    loggedIn: auth.loggedIn,
    email: auth.email,
    subscriptionType: auth.subscriptionType,
    authMethod: auth.authMethod,
  };
}
