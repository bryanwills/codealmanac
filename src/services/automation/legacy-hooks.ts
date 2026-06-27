import { cleanupLegacyHooks as cleanupPlatformLegacyHooks } from "../../platform/automation/legacy-hooks.js";

export interface CleanupLegacyAutomationHooksOptions {
  homeDir: string;
}

export async function cleanupLegacyAutomationHooks(
  options: CleanupLegacyAutomationHooksOptions,
): Promise<void> {
  await cleanupPlatformLegacyHooks(options);
}
