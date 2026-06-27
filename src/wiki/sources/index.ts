export {
  collectSourceHealthFindings,
  type SourceHealthFindings,
} from "./health.js";
export {
  applySourceFrontmatterFix,
  migrateLegacySourceFrontmatter,
  migrateLegacySourceFrontmatterInDb,
  writeSourceFrontmatterFix,
  type LegacySourceMigrationOptions,
  type LegacySourceMigrationResult,
  type SourceFrontmatterFixResult,
} from "./maintenance.js";
