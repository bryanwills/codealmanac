export {
  installAutomation,
  readAutomationStatus,
  uninstallAutomation,
} from "./automation.js";
export {
  defaultSyncAutomationPlistPath,
  parseAutomationTaskIds,
} from "./catalog.js";
export {
  cleanupLegacyAutomationHooks,
} from "./legacy-hooks.js";
export {
  migrateLegacyAutomation,
} from "./migration.js";
export type {
  AutomationInstallOptions,
  AutomationInstallResult,
  AutomationStatusOptions,
  AutomationStatusResult,
  AutomationStatusSection,
  AutomationUninstallOptions,
  AutomationUninstallResult,
  InstalledAutomationTask,
} from "./types.js";
export type {
  AutomationTaskId,
} from "./catalog.js";
export type {
  CleanupLegacyAutomationHooksOptions,
} from "./legacy-hooks.js";
export type {
  MigrateLegacyAutomationOptions,
  MigrateLegacyAutomationResult,
} from "./migration.js";
