import { resolveWikiRoot } from "../../wiki/indexer/resolve-wiki.js";
import {
  migrateLegacySourceFrontmatter,
  type LegacySourceMigrationResult,
} from "../../wiki/sources/index.js";

export interface MigrateLegacySourcesRequest {
  cwd: string;
  wiki?: string;
  topic?: string;
  stdinSlugs?: string[];
}

export interface MigrateLegacySourcesResult {
  migrated_pages: number;
  unfixable_sources: Array<{ slug: string; source: string }>;
}

export async function migrateLegacySources(
  request: MigrateLegacySourcesRequest,
): Promise<MigrateLegacySourcesResult> {
  const repoRoot = await resolveWikiRoot({
    cwd: request.cwd,
    wiki: request.wiki,
  });
  return migrationResultFromWikiSources(
    await migrateLegacySourceFrontmatter({
      repoRoot,
      topic: request.topic,
      stdinSlugs: request.stdinSlugs,
    }),
  );
}

function migrationResultFromWikiSources(
  result: LegacySourceMigrationResult,
): MigrateLegacySourcesResult {
  return {
    migrated_pages: result.migrated_pages,
    unfixable_sources: result.unfixable_sources.map((source) => ({
      slug: source.slug,
      source: source.source,
    })),
  };
}
