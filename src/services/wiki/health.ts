import { resolveWikiRoot } from "../../wiki/indexer/resolve-wiki.js";
import {
  collectHealthReport,
  DEFAULT_STALE_SECONDS,
  type HealthReport,
} from "../../wiki/health/index.js";

export interface CheckWikiHealthRequest {
  cwd: string;
  wiki?: string;
  topic?: string;
  staleSeconds: number;
  stdinSlugs?: string[];
}

export type WikiHealthReport = HealthReport;

export { DEFAULT_STALE_SECONDS };

export async function checkWikiHealth(
  request: CheckWikiHealthRequest,
): Promise<WikiHealthReport> {
  const repoRoot = await resolveWikiRoot({
    cwd: request.cwd,
    wiki: request.wiki,
  });
  return collectHealthReport({
    repoRoot,
    topic: request.topic,
    staleSeconds: request.staleSeconds,
    stdinSlugs: request.stdinSlugs,
  });
}
