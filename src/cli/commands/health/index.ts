import { BLUE, BOLD, DIM, GREEN, RED, RST } from "../../../ansi.js";
import { parseDuration } from "../../../wiki/indexer/duration.js";
import { resolveWikiRoot } from "../../../wiki/indexer/resolve-wiki.js";
import {
  applyHealthFixes,
  collectHealthReport,
  DEFAULT_STALE_SECONDS,
  type HealthReport,
} from "../../../wiki/health/index.js";

export interface HealthOptions {
  cwd: string;
  wiki?: string;
  topic?: string;
  stale?: string;
  stdin?: boolean;
  stdinInput?: string;
  json?: boolean;
  fix?: boolean;
}

export interface HealthCommandOutput {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export async function runHealth(
  options: HealthOptions,
): Promise<HealthCommandOutput> {
  const repoRoot = await resolveWikiRoot({ cwd: options.cwd, wiki: options.wiki });
  const staleSeconds = options.stale !== undefined
    ? parseDuration(options.stale)
    : DEFAULT_STALE_SECONDS;
  const slugs = stdinSlugs(options);
  if (options.fix === true) {
    await applyHealthFixes({
      repoRoot,
      topic: options.topic,
      stdinSlugs: slugs,
    });
  }
  const report = await collectHealthReport({
    repoRoot,
    topic: options.topic,
    staleSeconds,
    stdinSlugs: slugs,
  });

  if (options.json === true) {
    return {
      stdout: `${JSON.stringify(report, null, 2)}\n`,
      stderr: "",
      exitCode: 0,
    };
  }

  return {
    stdout: formatReport(report),
    stderr: "",
    exitCode: 0,
  };
}

function stdinSlugs(options: HealthOptions): string[] | undefined {
  if (options.stdin !== true || options.stdinInput === undefined) return undefined;
  const slugs: string[] = [];
  for (const line of options.stdinInput.split(/\r?\n/)) {
    const slug = line.trim();
    if (slug.length > 0) slugs.push(slug);
  }
  return slugs;
}

function formatReport(r: HealthReport): string {
  const sections: string[] = [];
  sections.push(
    section(
      "orphans",
      r.orphans.length,
      r.orphans.map((o) => `  ${BLUE}${o.slug}${RST}`),
    ),
  );
  sections.push(
    section(
      "stale",
      r.stale.length,
      r.stale.map((s) => `  ${BLUE}${s.slug}${RST}     ${DIM}(${s.days_since_update} days)${RST}`),
    ),
  );
  sections.push(
    section(
      "dead-refs",
      r.dead_refs.length,
      r.dead_refs.map((d) => `  ${BLUE}${d.slug}${RST}  references ${d.path} ${DIM}(missing)${RST}`),
    ),
  );
  sections.push(
    section(
      "broken-links",
      r.broken_links.length,
      r.broken_links.map(
        (b) => `  ${BLUE}${b.source_slug}${RST} → ${b.target_slug} ${DIM}(target does not exist)${RST}`,
      ),
    ),
  );
  sections.push(
    section(
      "broken-xwiki",
      r.broken_xwiki.length,
      r.broken_xwiki.map(
        (b) =>
          `  ${BLUE}${b.source_slug}${RST} → ${b.target_wiki}:${b.target_slug} ${DIM}(wiki unregistered or unreachable)${RST}`,
      ),
    ),
  );
  sections.push(
    section(
      "missing-sources",
      r.missing_sources.length,
      r.missing_sources.map((s) => `  ${BLUE}${s.slug}${RST} cites ${s.source_id} ${DIM}(missing source)${RST}`),
    ),
  );
  sections.push(
    section(
      "unused-sources",
      r.unused_sources.length,
      r.unused_sources.map((s) => `  ${BLUE}${s.slug}${RST} lists ${s.source_id} ${DIM}(not cited)${RST}`),
    ),
  );
  sections.push(
    section(
      "legacy-frontmatter",
      r.legacy_frontmatter.length,
      r.legacy_frontmatter.map((s) => `  ${BLUE}${s.slug}${RST} uses ${s.fields.join(", ")}`),
    ),
  );
  sections.push(
    section(
      "unfixable-sources",
      r.unfixable_sources.length,
      r.unfixable_sources.map((s) => `  ${BLUE}${s.slug}${RST} has ambiguous legacy source ${s.source}`),
    ),
  );
  sections.push(
    section(
      "duplicate-sources",
      r.duplicate_sources.length,
      r.duplicate_sources.map((s) => `  ${BLUE}${s.slug}${RST} repeats ${s.source_id}`),
    ),
  );
  sections.push(
    section(
      "empty-topics",
      r.empty_topics.length,
      r.empty_topics.map((e) => `  ${BLUE}${e.slug}${RST}`),
    ),
  );
  sections.push(
    section(
      "empty-pages",
      r.empty_pages.length,
      r.empty_pages.map((e) => `  ${BLUE}${e.slug}${RST}`),
    ),
  );
  sections.push(
    section(
      "slug-collisions",
      r.slug_collisions.length,
      r.slug_collisions.map((c) => `  ${BLUE}${c.slug}${RST}: ${c.paths.join(", ")}`),
    ),
  );
  return `${sections.join("\n\n")}\n`;
}

function section(label: string, count: number, lines: string[]): string {
  if (count === 0) return `${BOLD}${label}${RST} ${GREEN}(0): (ok)${RST}`;
  return `${BOLD}${label}${RST} ${RED}(${count})${RST}:\n${lines.join("\n")}`;
}
